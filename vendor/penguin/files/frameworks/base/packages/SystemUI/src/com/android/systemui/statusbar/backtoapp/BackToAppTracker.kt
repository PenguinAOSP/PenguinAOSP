/*
 * Copyright (C) 2026 The PenguinOS Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.systemui.statusbar.backtoapp

import android.app.ActivityManager.RunningTaskInfo
import android.app.ActivityOptions
import android.app.ActivityTaskManager.INVALID_TASK_ID
import android.app.WindowConfiguration.ACTIVITY_TYPE_ASSISTANT
import android.app.WindowConfiguration.ACTIVITY_TYPE_DREAM
import android.app.WindowConfiguration.ACTIVITY_TYPE_HOME
import android.app.WindowConfiguration.ACTIVITY_TYPE_RECENTS
import android.content.Context
import android.content.Intent
import android.database.ContentObserver
import android.graphics.drawable.Drawable
import android.os.Handler
import android.os.Looper
import android.os.UserHandle
import android.provider.Settings
import android.util.Log
import com.android.systemui.shared.system.ActivityManagerWrapper
import com.android.systemui.shared.system.TaskStackChangeListener
import com.android.systemui.shared.system.TaskStackChangeListeners
import java.util.concurrent.Executors
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Tracks the previous non-system task so the status bar can offer "back to app".
 *
 * UwUAOSP TaskInfo lacks penguinOS's launchedFromTaskId/launchedFromPackage fields, so this
 * keeps the previous app from TaskStackChangeListener instead.
 */
class BackToAppTracker private constructor(context: Context) {

    data class Target(
        val taskId: Int,
        val packageName: String,
        val label: CharSequence,
        val icon: Drawable?,
    )

    private val appContext = context.applicationContext
    private val mainHandler = Handler(Looper.getMainLooper())
    private val worker = Executors.newSingleThreadExecutor { Thread(it, "BackToApp") }

    private val _target = MutableStateFlow<Target?>(null)
    val target: StateFlow<Target?> = _target.asStateFlow()

    private var lastTopTaskId = INVALID_TASK_ID
    private var previousApp: Target? = null
    @Volatile private var enabled = false

    private val listener =
        object : TaskStackChangeListener {
            override fun onTaskStackChanged() = refresh()

            override fun onTaskMovedToFront(taskInfo: RunningTaskInfo) = refresh()

            override fun onTaskRemoved(taskId: Int) {
                worker.execute {
                    if (previousApp?.taskId == taskId) previousApp = null
                    if (_target.value?.taskId == taskId) _target.value = null
                }
            }
        }

    init {
        val resolver = appContext.contentResolver
        val observer =
            object : ContentObserver(mainHandler) {
                override fun onChange(selfChange: Boolean) = readEnabled()
            }
        resolver.registerContentObserver(
            Settings.System.getUriFor(Settings.System.BACK_TO_APP_INDICATOR),
            false,
            observer,
            UserHandle.USER_ALL,
        )
        readEnabled()
        TaskStackChangeListeners.getInstance().registerTaskStackListener(listener)
    }

    private fun readEnabled() {
        enabled =
            Settings.System.getIntForUser(
                appContext.contentResolver,
                Settings.System.BACK_TO_APP_INDICATOR,
                0,
                UserHandle.USER_CURRENT,
            ) != 0
        refresh()
    }

    private fun refresh() {
        worker.execute {
            if (!enabled) {
                lastTopTaskId = INVALID_TASK_ID
                previousApp = null
                _target.value = null
                return@execute
            }
            val top = ActivityManagerWrapper.getInstance().getRunningTask() ?: return@execute
            update(top)
        }
    }

    private fun update(top: RunningTaskInfo) {
        val taskId = top.taskId
        if (top.isSystemSurface()) {
            lastTopTaskId = taskId
            _target.value = null
            return
        }

        val pkg = top.topActivity?.packageName ?: run {
            _target.value = null
            return
        }

        if (taskId != lastTopTaskId) {
            val show = previousApp?.takeIf { it.taskId != taskId }
            _target.value = show
            previousApp = describe(taskId, pkg, top.userId)
            lastTopTaskId = taskId
            if (DEBUG) {
                Log.d(TAG, "top=$taskId $pkg show=${show?.packageName}")
            }
            return
        }

        val remembered = previousApp
        _target.value =
            if (remembered != null && remembered.taskId != taskId) remembered else null
    }

    private fun describe(taskId: Int, packageName: String, userId: Int): Target? =
        try {
            val pm = appContext.packageManager
            val info = pm.getApplicationInfoAsUser(packageName, 0, userId)
            Target(taskId, packageName, pm.getApplicationLabel(info), pm.getApplicationIcon(info))
        } catch (e: Exception) {
            Log.w(TAG, "No app to go back to for $packageName", e)
            null
        }

    fun goBack(target: Target) {
        worker.execute {
            val options = ActivityOptions.makeBasic()
            if (
                ActivityManagerWrapper.getInstance()
                    .startActivityFromRecents(target.taskId, options)
            ) {
                return@execute
            }
            appContext.packageManager.getLaunchIntentForPackage(target.packageName)?.let { intent ->
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                mainHandler.post { appContext.startActivityAsUser(intent, UserHandle.CURRENT) }
            }
            _target.value = null
        }
    }

    private fun RunningTaskInfo.isSystemSurface(): Boolean =
        when (topActivityType) {
            ACTIVITY_TYPE_HOME,
            ACTIVITY_TYPE_RECENTS,
            ACTIVITY_TYPE_ASSISTANT,
            ACTIVITY_TYPE_DREAM -> true
            else -> false
        }

    companion object {
        private const val TAG = "BackToAppTracker"
        private val DEBUG = Log.isLoggable(TAG, Log.DEBUG)

        @Volatile private var instance: BackToAppTracker? = null

        fun get(context: Context): BackToAppTracker =
            instance
                ?: synchronized(this) {
                    instance ?: BackToAppTracker(context).also { instance = it }
                }
    }
}

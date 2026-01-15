// src/lib/stores/timerStore.ts
import { writable, derived, get } from "svelte/store";
import { groupStatuses } from "./groupStore";

// Store for elapsed seconds per group
export const groupTimers = writable({
  "1": 0,
  "2": 0,
  "3": 0,
});

// Track interval IDs
let timerIntervals = {};

// Reset all timers to 0 on page load/refresh
if (typeof window !== "undefined") {
  groupTimers.set({
    "1": 0,
    "2": 0,
    "3": 0,
  });
}

// Start timer for a specific group
export function startTimer(groupId) {
  const id = groupId.toString();

  // Clear existing interval if any
  if (timerIntervals[id]) {
    clearInterval(timerIntervals[id]);
  }

  // Start new interval
  timerIntervals[id] = setInterval(() => {
    groupTimers.update((timers) => ({
      ...timers,
      [id]: timers[id] + 1,
    }));
  }, 1000);
}

// Stop timer for a specific group
export function stopTimer(groupId) {
  const id = groupId.toString();

  if (timerIntervals[id]) {
    clearInterval(timerIntervals[id]);
    delete timerIntervals[id];
  }
}

// Reset timer for a specific group
export function resetTimer(groupId) {
  const id = groupId.toString();

  stopTimer(groupId);
  groupTimers.update((timers) => ({
    ...timers,
    [id]: 0,
  }));
}

// Pause timer (just stop without reset)
export function pauseTimer(groupId) {
  stopTimer(groupId);
}

// Format seconds to HH:MM:SS
export function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

// Clean up all timers (call on app unmount)
export function cleanupAllTimers() {
  Object.keys(timerIntervals).forEach((id) => {
    clearInterval(timerIntervals[id]);
  });
  timerIntervals = {};
}

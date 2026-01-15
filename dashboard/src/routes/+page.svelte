<script>
    import GroupInfo from "$lib/components/groupInfo/groupInfo.svelte";
    import { groupStatuses, updateGroupStatus } from "$lib/stores/groupStore";
    import {
        startTimer,
        stopTimer,
        pauseTimer,
        resetTimer,
        cleanupAllTimers,
    } from "$lib/stores/timerStore";
    import { onMount } from "svelte";

    let groups = ["1", "2", "3"];
    const sockets = new Map();

    onMount(() => {
        for (let group of groups) {
            const ws = new WebSocket(`ws://localhost:8000/ws/dev${group}`);
            ws.onmessage = (event) => {
                console.log(event);
            };
            sockets.set(group, ws);
        }

        return () => {
            for (let group of groups) {
                sockets.get(group).close();
            }
        };
    });
    function handleStart() {
        for (let group of groups) {
            updateGroupStatus(group, "recording");
            startTimer(group);
            sockets.get(group).send("1");
        }
    }

    function handleStop() {
        for (let group of groups) {
            updateGroupStatus(group, "stopped");
            resetTimer(group);
            sockets.get(group).send("2");
        }
    }

    function handlePause() {
        for (let group of groups) {
            updateGroupStatus(group, "paused");
            pauseTimer(group);
            sockets.get(group).send("3");
        }
    }

    function handleAnalyze() {
        for (let group of groups) {
            updateGroupStatus(group, "analyzing");
            stopTimer(group);
            sockets.get(group).send("4");
        }
    }
</script>

<div class="flex flex-col items-center">
    <div class="w-full h-24 bg-blue-900">
        <div class="flex gap-4 flex-wrap">
            <button
                onclick={handleStart}
                class="px-6 py-3 bg-white border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 font-semibold transition-colors disabled:opacity-50"
            >
                Start
            </button>

            <button
                onclick={handlePause}
                class="px-6 py-3 bg-white border-2 border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 font-semibold transition-colors disabled:opacity-50"
            >
                Pause
            </button>

            <button
                onclick={handleStop}
                class="px-6 py-3 bg-white border-2 border-red-500 text-red-600 rounded-lg hover:bg-red-50 font-semibold transition-colors disabled:opacity-50"
            >
                Stop
            </button>

            <button
                onclick={handleAnalyze}
                class="px-6 py-3 bg-white border-2 border-grey-500 text-grey-600 rounded-lg hover:bg-grey-50 font-semibold transition-colors disabled:opacity-50"
            >
                Analyze
            </button>
        </div>
    </div>
    <div class="grid grid-cols-2 grid-rows-2 w-full gap-4 p-4">
        <GroupInfo status={$groupStatuses["1"]} groupId={1} />
        <GroupInfo status={$groupStatuses["2"]} groupId={2} />
        <GroupInfo status={$groupStatuses["3"]} groupId={3} />
    </div>
</div>

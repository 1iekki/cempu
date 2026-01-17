<script>
    import GroupInfo from "$lib/components/groupInfo/groupInfo.svelte";
    import { groupStatuses, updateGroupStatus } from "$lib/stores/groupStore";
    import {
        startTimer,
        stopTimer,
        pauseTimer,
        resetTimer,
    } from "$lib/stores/timerStore";
    import { updateAnalysisResult } from "$lib/stores/analysisStore";
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

    async function analyzeGroup(groupId) {
        try {
            // Clear previous result
            updateAnalysisResult(groupId, null, null);

            // Start the analysis
            const startResponse = await fetch(
                `http://localhost:8000/analyze/dev${groupId}`,
                { method: "POST" },
            );

            if (!startResponse.ok) {
                throw new Error("Failed to start analysis");
            }

            // Poll for results until we get one
            while (true) {
                await new Promise((resolve) => setTimeout(resolve, 1000));

                const getResponse = await fetch(
                    `http://localhost:8000/analyze/dev${groupId}`,
                    { method: "GET" },
                );

                const result = await getResponse.text();
                const trimmedResult = result.trim();
                console.log(`Group ${groupId} analysis status:`, trimmedResult);

                // Check if result is a valid number
                const parsedScore = parseFloat(trimmedResult);

                if (!isNaN(parsedScore)) {
                    // Got a valid number - analysis complete
                    updateAnalysisResult(groupId, parsedScore, null);
                    updateGroupStatus(groupId, "stopped");
                    break;
                }
            }
        } catch (error) {
            console.error(`Group ${groupId} analysis error:`, error);
            const errorMsg =
                error instanceof Error ? error.message : "Analysis failed";
            updateAnalysisResult(groupId, null, errorMsg);
            updateGroupStatus(groupId, "stopped");
        }
    }

    async function handleAnalyze() {
        for (let group of groups) {
            updateGroupStatus(group, "analyzing");
            stopTimer(group);
            sockets.get(group).send("4");
        }
        const analysisPromises = groups.map((group) => analyzeGroup(group));
        await Promise.all(analysisPromises);
    }
</script>

<div class="flex flex-col items-center">
    <div class="w-full h-24 bg-blue-900 flex justify-center items-center">
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

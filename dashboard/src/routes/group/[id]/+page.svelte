<script lang="ts">
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { groupTimers, formatTime } from "$lib/stores/timerStore";
    import {
        startTimer,
        stopTimer,
        pauseTimer,
        resetTimer,
    } from "$lib/stores/timerStore";
    import {
        groupAnalysisResults,
        updateAnalysisResult,
    } from "$lib/stores/analysisStore";
    import { groupStatuses, updateGroupStatus } from "$lib/stores/groupStore";

    let groupId = $derived($page.params.id!);

    let analysisData = $derived(
        $groupAnalysisResults[groupId] || {
            context_score: null,
            engagement_score: null,
            error: null,
        },
    );

    let engagement = $state(-1);
    let status = $state<"recording" | "paused" | "stopped" | "analyzing">(
        $groupStatuses[groupId] || "stopped",
    );
    let socket: WebSocket;
    let intervalId: ReturnType<typeof setInterval> | undefined;

    $effect(() => {
        updateGroupStatus(groupId, status);
    });

    const variants = {
        recording: {
            borderColor: "border-l-green-500",
            statusText: "Recording",
            statusColor: "text-green-600",
        },
        paused: {
            borderColor: "border-l-blue-500",
            statusText: "Paused",
            statusColor: "text-blue-600",
        },
        stopped: {
            borderColor: "border-l-red-500",
            statusText: "Stopped",
            statusColor: "text-red-600",
        },
        analyzing: {
            borderColor: "border-l-grey-500",
            statusText: "Analyzing",
            statusColor: "text-grey-600",
        },
    };

    let currentVariant = $derived(variants[status]);

    onMount(() => {
        socket = new WebSocket(`ws://localhost:8000/ws/dev${groupId}`);

        socket.onmessage = (event) => {
            console.log(event);
            engagement = Number(event.data);
        };

        return () => {
            socket.close();
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    });

    function goBack() {
        goto("/");
    }

    function handleStart() {
        status = "recording";
        socket.send("1");
        startTimer(groupId);
        clearInterval(intervalId);
    }

    function handleStop() {
        status = "stopped";
        stopTimer(groupId);
        socket.send("2");
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = undefined;
        }
    }

    function handlePause() {
        status = "paused";
        pauseTimer(groupId);
        socket.send("3");
    }

    async function handleAnalyze() {
        status = "analyzing";
        stopTimer(groupId);
        socket.send("4");

        // Clear previous result
        updateAnalysisResult(groupId, null, null, null);

        try {
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
                console.log("Analysis status:", trimmedResult);

                // Try to parse as JSON
                try {
                    const parsedResult = JSON.parse(trimmedResult);

                    // Check if we got valid scores
                    if (
                        parsedResult.context_score !== undefined &&
                        parsedResult.engagement_score !== undefined
                    ) {
                        // Got valid result - analysis complete
                        updateAnalysisResult(
                            groupId,
                            parsedResult.context_score,
                            parsedResult.engagement_score,
                            null,
                        );
                        status = "stopped";
                        break;
                    }
                } catch (e) {
                    // Not JSON yet, keep polling
                    console.log("Waiting for result...");
                }
            }
        } catch (error) {
            console.error("Analysis error:", error);
            const errorMsg =
                error instanceof Error ? error.message : "Analysis failed";
            updateAnalysisResult(groupId, null, null, errorMsg);
            status = "stopped";
        }
    }

    let timer = $derived($groupTimers[groupId.toString()]);
</script>

<div class="w-full h-24 bg-blue-900 flex items-center px-8">
    <button
        onclick={goBack}
        class="px-6 py-3 bg-white text-blue-900 rounded-lg hover:bg-blue-50 font-semibold transition-colors"
    >
        Back
    </button>
</div>
<div class="min-h-screen bg-gray-50 p-8">
    <div
        class="bg-white rounded-lg shadow-lg p-8 border-l-16 transition-all duration-300 {currentVariant.borderColor}"
    >
        <h1 class="text-3xl font-bold mb-6">Group {groupId} Details</h1>

        <div class="space-y-4 mb-6">
            <div>
                <h2 class="text-xl font-semibold text-gray-700">Status</h2>
                <p
                    class="text-lg font-semibold {currentVariant.statusColor} transition-colors duration-300"
                >
                    {currentVariant.statusText}
                </p>
            </div>

            <div>
                <h2 class="text-xl font-semibold text-gray-700">
                    Engagement Score
                </h2>
                <p class="text-lg">
                    {#if engagement >= 0 && engagement <= 33}
                        low
                    {:else if engagement >= 34 && engagement <= 66}
                        average
                    {:else if engagement >= 67 && engagement <= 100}
                        high
                    {:else}
                        n/a
                    {/if}
                </p>
            </div>
            <div>
                <h2 class="text-xl font-semibold text-gray-700">
                    Analysis Result
                </h2>
                {#if status === "analyzing"}
                    <p class="text-lg text-purple-500 animate-pulse">
                        Analyzing...
                    </p>
                {:else if analysisData.context_score !== null && analysisData.engagement_score !== null}
                    <div class="space-y-1">
                        <p class="text-lg">
                            <span class="font-semibold">Context Score:</span>
                            <span class="text-green-600 font-semibold"
                                >{analysisData.context_score.toFixed(2)}</span
                            >
                        </p>
                        <p class="text-lg">
                            <span class="font-semibold">Diarization Score:</span
                            >
                            <span class="text-green-600 font-semibold"
                                >{analysisData.engagement_score.toFixed(
                                    2,
                                )}</span
                            >
                        </p>
                    </div>
                {:else if analysisData.error}
                    <p class="text-lg text-red-600">{analysisData.error}</p>
                {:else}
                    <p class="text-lg text-gray-400">No analysis yet</p>
                {/if}
            </div>

            <div>
                <h2 class="text-xl font-semibold text-gray-700">Time</h2>
                <p class="text-lg">{formatTime(timer)}</p>
            </div>
        </div>

        <!-- Buttons -->
        <div class="flex gap-4 flex-wrap">
            <button
                onclick={handleStart}
                disabled={status === "recording" || status === "analyzing"}
                class="px-6 py-3 bg-white border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 font-semibold transition-colors disabled:opacity-50"
            >
                Start
            </button>

            <button
                onclick={handlePause}
                disabled={status !== "recording"}
                class="px-6 py-3 bg-white border-2 border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 font-semibold transition-colors disabled:opacity-50"
            >
                Pause
            </button>

            <button
                onclick={handleStop}
                disabled={status === "stopped"}
                class="px-6 py-3 bg-white border-2 border-red-500 text-red-600 rounded-lg hover:bg-red-50 font-semibold transition-colors disabled:opacity-50"
            >
                Stop
            </button>

            <button
                onclick={handleAnalyze}
                disabled={status === "analyzing"}
                class="px-6 py-3 bg-white border-2 border-grey-500 text-grey-600 rounded-lg hover:bg-grey-50 font-semibold transition-colors disabled:opacity-50"
            >
                Analyze
            </button>
        </div>
    </div>
</div>

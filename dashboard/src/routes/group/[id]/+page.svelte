<script lang="ts">
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { groupStatuses, updateGroupStatus } from "$lib/stores/groupStore";

    let groupId = $derived($page.params.id!);

    let engagement = $state(0);
    let status = $state<"recording" | "paused" | "stopped" | "analyzing">($groupStatuses[groupId] || "stopped");
    let socket: WebSocket;

    $effect(() => {
        updateGroupStatus(groupId, status);
    });

    const variants = {
        recording: {
            borderColor: "border-l-green-500",
            statusText: "Recording",
            statusColor: "text-green-600"
        },
        paused: {
            borderColor: "border-l-blue-500",
            statusText: "Paused",
            statusColor: "text-blue-600"
        },
        stopped: {
            borderColor: "border-l-red-500",
            statusText: "Stopped",
            statusColor: "text-red-600"
        },
        analyzing: {
            borderColor: "border-l-grey-500",
            statusText: "Analyzing",
            statusColor: "text-grey-600"
        }
    };

    let currentVariant = $derived(variants[status]);
    
    onMount(() => {
        socket = new WebSocket(`ws://localhost:8000/ws/dev${groupId}`);

        socket.onmessage = (event) => {
            console.log(event);
            engagement = Number(event.data);
        };

        return () => socket.close();
    });

    function goBack() {
        goto("/");
    }

    function handleStart() {
        status = "recording";
        socket.send("1");
    }

    function handleStop() {
        status = "stopped";
        socket.send("2");
    }

    function handlePause() {
        status = "paused";
        socket.send("3");
    }

    function handleAnalyze() {
        status = "analyzing";
        socket.send("4");
    }
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
        class="bg-white rounded-lg shadow-lg p-8 border-l-[16px] transition-all duration-300 {currentVariant.borderColor}"
    >
        <h1 class="text-3xl font-bold mb-6">Group {groupId} Details</h1>

        <div class="space-y-4 mb-6">
            <div>
                <h2 class="text-xl font-semibold text-gray-700">Status</h2>
                <p class="text-lg font-semibold {currentVariant.statusColor} transition-colors duration-300">
                    {currentVariant.statusText}
                </p>
            </div>

            <div>
                <h2 class="text-xl font-semibold text-gray-700">
                    Engagement Score
                </h2>
                <p class="text-lg">{engagement}</p>
            </div>

            <div>
                <h2 class="text-xl font-semibold text-gray-700">Time</h2>
                <p class="text-lg">00:12:13</p>
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

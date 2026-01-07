<script lang="ts">
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";

    let groupId = $derived($page.params.id);

    let engagement = $state(0);
    let status = $state("recording");

    onMount(() => {
        const socket = new WebSocket(`ws://localhost:8000/ws/group/${groupId}`);

        socket.onmessage = (event) => {
            console.log(event);
            engagement = Number(event.data);
        };

        return () => socket.close();
    });

    function goBack() {
        goto("/");
    }

    function handleStart() {}

    function handleStop() {}

    function handlePause() {}

    function handleAnalyze() {}
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
        class="bg-white rounded-lg shadow-lg p-8 border-l-[16px] border-l-green-500"
    >
        <h1 class="text-3xl font-bold mb-6">Group {groupId} Details</h1>

        <div class="space-y-4 mb-6">
            <div>
                <h2 class="text-xl font-semibold text-gray-700">Status</h2>
                <p class="text-lg">Recording</p>
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
                class="px-6 py-3 bg-white border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 font-semibold transition-colors"
            >
                Start
            </button>

            <button
                onclick={handlePause}
                class="px-6 py-3 bg-white border-2 border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 font-semibold transition-colors"
            >
                Pause
            </button>

            <button
                onclick={handleStop}
                class="px-6 py-3 bg-white border-2 border-red-500 text-red-600 rounded-lg hover:bg-red-50 font-semibold transition-colors"
            >
                Stop
            </button>

            <button
                onclick={handleAnalyze}
                class="px-6 py-3 bg-white border-2 border-grey-500 text-grey-600 rounded-lg hover:bg-purple-50 font-semibold transition-colors"
            >
                Analyze
            </button>
        </div>
    </div>
</div>

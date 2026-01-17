<script lang="ts">
    import { tv, type VariantProps } from "tailwind-variants";
    import type { Snippet } from "svelte";
    import { goto } from "$app/navigation";
    import { groupTimers, formatTime } from "$lib/stores/timerStore";
    import { groupAnalysisResults } from "$lib/stores/analysisStore";

    const groupVariants = tv({
        base: "grid grid-cols-2 grid-rows-3 rounded-md p-4 bg-gray-100 shadow-lg border-l-[20px] transition-all hover:shadow-xl",
        variants: {
            status: {
                recording: "border-l-green-500 bg-green-50",
                paused: "border-l-blue-500 bg-blue-50",
                stopped: "border-l-red-500 bg-red-50",
                analyzing: "border-l-grey-500 bg-grey-50",
            },
        },
        defaultVariants: {
            status: "recording",
        },
    });
    type Variants = VariantProps<typeof groupVariants>;

    let {
        children,
        class: className,
        status = "recording",
        groupId = 1,
        ...rest
    }: {
        children?: Snippet;
        class?: string;
        status?: Variants["status"];
        groupId?: number;
        [key: string]: any;
    } = $props();

    const statusTextMap = {
        recording: "On",
        paused: "Paused",
        stopped: "Off",
        analyzing: "Analyzing",
    };

    let displayStatus = $derived(statusTextMap[status]);

    import { onMount } from "svelte";

    let engagement = $state(0);

    onMount(() => {
        const socket = new WebSocket(`ws://localhost:8000/ws/dev${groupId}`);

        socket.onmessage = (event) => {
            console.log(event);
            engagement = Number(event.data);
        };

        return () => socket.close();
    });

    function handleClick() {
        goto(`/group/${groupId}`);
    }
    let timer = $derived($groupTimers[groupId.toString()]);

    let analysisData = $derived(
        $groupAnalysisResults[groupId.toString()] || {
            score: null,
            error: null,
        },
    );
</script>

<div
    class={groupVariants({ status, class: className })}
    onclick={handleClick}
    role="button"
    tabindex="0"
    onkeydown={(e) => e.key === "Enter" && handleClick()}
    {...rest}
>
    <p>Group: {groupId}</p>
    <p class="text-right">Status: {displayStatus}</p>
    <p class="col-span-2">
        Engagement score: {#if engagement >= 0 && engagement <= 33}
            low
        {:else if engagement >= 34 && engagement <= 66}
            average
        {:else if engagement >= 67 && engagement <= 100}
            high
        {/if}
    </p>
    <p class="col-span-2">
        Analysis:
        {#if status === "analyzing"}
            <span class="text-purple-600 animate-pulse">Analyzing...</span>
        {:else if analysisData.score !== null}
            <span class="text-green-600 font-semibold"
                >{analysisData.score.toFixed(2)}</span
            >
        {:else if analysisData.error}
            <span class="text-red-600">{analysisData.error}</span>
        {:else}
            <span class="text-gray-400">Not analyzed</span>
        {/if}
    </p>
    <p class="col-span-2">Time: {formatTime(timer)}</p>
</div>

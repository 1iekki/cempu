<script lang="ts">
    import { tv, type VariantProps } from "tailwind-variants";
    import type { Snippet } from "svelte";
    const groupVariants = tv({
        base: "grid grid-cols-2 grid-rows-3 rounded-md p-4",
        variants: {
            status: {
                recording: "bg-green-500",
                paused: "bg-blue-500",
                stopped: "bg-red-500",
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
        ...rest
    }: {
        children?: Snippet;
        class?: string;
        status?: Variants["status"];
        [key: string]: any;
    } = $props();

    const statusTextMap = {
        recording: "On",
        paused: "Paused",
        stopped: "Off",
    };

    let displayStatus = $derived(statusTextMap[status]);

    import { onMount } from "svelte";

    let engagement = $state(0);

    onMount(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");

        socket.onmessage = (event) => {
            console.log(event);
            engagement = Number(event.data);
        };

        return () => socket.close();
    });
</script>

<div class={groupVariants({ status, class: className })} {...rest}>
    <p>Group: 1</p>
    <p class="text-right">Status: {displayStatus}</p>
    <p class="col-span-2">Engagement score: {engagement}</p>
    <p class="col-span-2">Time: 00:12:13</p>
</div>

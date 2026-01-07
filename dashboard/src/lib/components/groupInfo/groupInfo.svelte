<script lang="ts">
    import { tv, type VariantProps } from "tailwind-variants";
    import type { Snippet } from "svelte";
    import { goto } from "$app/navigation";

    const groupVariants = tv({
        base: "grid grid-cols-2 grid-rows-3 rounded-md p-4 bg-gray-100 shadow-lg border-l-[20px]",
        variants: {
            status: {
                recording: "border-l-green-500 bg-green-50",
                paused: "border-l-blue-500 bg-blue-50",
                stopped: "border-l-red-500 bg-red-50",
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
    <p class="col-span-2">Engagement score: {engagement}</p>
    <p class="col-span-2">Time: 00:12:13</p>
</div>

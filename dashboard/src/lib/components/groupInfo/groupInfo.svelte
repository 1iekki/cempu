<script lang="ts">
    import type { Snippet } from "svelte";
    import { groupVariants, type GroupVariants } from "./groupInfo.variants";
    let {
        children,
        class: className,
        status = "recording",
        groupName,
        deviceName,
        ...rest
    }: {
        children?: Snippet;
        class?: string;
        status?: GroupVariants["status"];
        groupName?: string;
        deviceName?: string;
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

    import mqtt from "mqtt";
    import type { MqttClient } from "mqtt";
    let client: MqttClient;

    onMount(() => {
        client = mqtt.connect("ws://localhost:9001");

        client.on("connect", () => {
            console.log("MQTT connected");

            client.subscribe(`CEMPU/${deviceName}/engagement`, (err) => {
                if (!err) {
                    client.publish(
                        `CEMPU/${deviceName}/engagement`,
                        `Hello mqtt ${deviceName}`,
                    );
                }
            });
        });

        client.on("message", (topic, message) => {
            console.log(topic, message.toString());
            engagement = Number(message.toString());
        });

        return () => {
            client?.end();
        };
    });
</script>

<div class={groupVariants({ status, class: className })} {...rest}>
    <p>Group: {groupName}</p>
    <p class="text-right">Status: {displayStatus}</p>
    <p class="col-span-2">Engagement score: {engagement}</p>
    <p class="col-span-2">Time: 00:12:13</p>
</div>

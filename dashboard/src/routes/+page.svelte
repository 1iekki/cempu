<script lang="ts">
    import GroupInfo from "$lib/components/groupInfo/groupInfo.svelte";
    const groupNames = ["1", "2", "3", "4"];
    const devicesNames = ["dev1", "dev2", "dev3", "dev4"];

    import mqtt from "mqtt";
    import type { MqttClient } from "mqtt";
    import { onMount } from "svelte";
    let client: MqttClient;

    // onMount(() => {
    //     client = mqtt.connect("ws://localhost:9001");

    //     client.on("connect", () => {
    //         console.log("MQTT connected");

    //         client.subscribe("CEMPU/dev3/engagement", (err) => {
    //             if (!err) {
    //                 // client.publish("CEMPU/dev3/engagement", "Hello mqtt");
    //             }
    //         });
    //     });

    //     // client.on("message", (topic, message) => {
    //     //     console.log(topic, message.toString());
    //     // });

    //     return () => {
    //         client?.end();
    //     };
    // });
</script>

<div class="grid items-center">
    <div class="grid grid-cols-2 grid-rows-2 w-full gap-4 p-4">
        {#each groupNames as groupName, i}
            <a href="http://localhost:5173/group/{i + 1}"
                ><GroupInfo {groupName} deviceName={devicesNames[i]}
                ></GroupInfo></a
            >
        {/each}
        <!-- <GroupInfo groupName="4" deviceName="4" status="paused"></GroupInfo> -->
    </div>
</div>

<script>
    import GroupInfo from "$lib/components/groupInfo/groupInfo.svelte";
</script>

<div class="flex flex-col items-center">
    <div class="w-full h-24 bg-blue-900"></div>
    <div class="grid grid-cols-2 grid-rows-2 w-full gap-4 p-4">
        <GroupInfo status="recording" groupId={1} />
        <GroupInfo status="paused" groupId={2} />
        <GroupInfo status="stopped" groupId={3} />
    </div>
</div>

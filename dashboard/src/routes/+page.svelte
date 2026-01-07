<script>
    import GroupInfo from "$lib/components/groupInfo/groupInfo.svelte";
    import { groupStatuses } from "$lib/stores/groupStore";
</script>

<div class="flex flex-col items-center">
    <div class="w-full h-24 bg-blue-900"></div>
    <div class="grid grid-cols-2 grid-rows-2 w-full gap-4 p-4">
        <GroupInfo status={$groupStatuses['1']} groupId={1} />
        <GroupInfo status={$groupStatuses['2']} groupId={2} />
        <GroupInfo status={$groupStatuses['3']} groupId={3} />
    </div>
</div>

import { writable } from 'svelte/store';

type Status = "recording" | "paused" | "stopped" | "analyzing";

interface GroupStatus {
    [groupId: string]: Status;
}

const initialStatuses: GroupStatus = {
    '1': 'stopped',
    '2': 'stopped',
    '3': 'stopped'
};

export const groupStatuses = writable<GroupStatus>(initialStatuses);

export function updateGroupStatus(groupId: string, status: Status) {
    groupStatuses.update(statuses => ({
        ...statuses,
        [groupId]: status
    }));
}
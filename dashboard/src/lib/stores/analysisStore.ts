import { writable } from "svelte/store";

export const groupAnalysisResults = writable<
  Record<
    string,
    {
      score: number | null;
      error: string | null;
    }
  >
>({});

export function updateAnalysisResult(
  groupId: string,
  score: number | null,
  error: string | null = null,
) {
  groupAnalysisResults.update((results) => ({
    ...results,
    [groupId]: {
      score,
      error,
    },
  }));
}
export function getAnalysisResult(groupId: string) {
  let result:
    | { score: number | null; error: string | null; timestamp: number | null }
    | undefined;
  groupAnalysisResults.subscribe((results) => {
    result = results[groupId];
  })();
  return result;
}

// Function to clear analysis result
export function clearAnalysisResult(groupId: string) {
  groupAnalysisResults.update((results) => {
    const newResults = { ...results };
    delete newResults[groupId];
    return newResults;
  });
}

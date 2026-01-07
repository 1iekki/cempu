import { tv, type VariantProps } from "tailwind-variants";

export const groupVariants = tv({
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

export type GroupVariants = VariantProps<typeof groupVariants>;

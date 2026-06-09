"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { AdBanner } from "@/components/ads";

interface DismissibleStickyBannerProps {
  adKey?: string;
}

export function DismissibleStickyBanner({ adKey }: DismissibleStickyBannerProps) {
  const [dismissed, setDismissed] = useState(false);

  if (!adKey || adKey === "0" || dismissed) {
    return null;
  }

  return (
    <div className="sticky top-20 z-20 py-2">
      <div className="relative mx-auto max-w-4xl pr-10">
        <AdBanner type="banner-320x50" adKey={adKey} eager />
        <button
          type="button"
          aria-label="Close ad"
          onClick={() => setDismissed(true)}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full border border-border/80 bg-background/95 p-1 text-muted-foreground shadow-sm transition-colors hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";

interface UseDeferredAdSlotOptions {
  enabled: boolean;
  rootMargin?: string;
  delayMs?: number;
}

export function useDeferredAdSlot<T extends HTMLElement>({
  enabled,
  rootMargin = "320px 0px",
  delayMs = 0,
}: UseDeferredAdSlotOptions) {
  const ref = useRef<T>(null);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (!enabled || isActive) {
      return;
    }

    let timeoutId: number | undefined;
    const activate = () => {
      if (delayMs > 0) {
        timeoutId = window.setTimeout(() => setIsActive(true), delayMs);
        return;
      }
      setIsActive(true);
    };

    const node = ref.current;
    if (!node || typeof IntersectionObserver === "undefined") {
      activate();
      return () => {
        if (timeoutId) window.clearTimeout(timeoutId);
      };
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          observer.disconnect();
          activate();
        }
      },
      { rootMargin },
    );

    observer.observe(node);

    return () => {
      observer.disconnect();
      if (timeoutId) window.clearTimeout(timeoutId);
    };
  }, [delayMs, enabled, isActive, rootMargin]);

  return { ref, isActive };
}

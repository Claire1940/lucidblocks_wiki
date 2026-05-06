"use client";

import { useEffect, useRef } from "react";
import { useDeferredAdSlot } from "./useDeferredAdSlot";

interface NativeBannerAdProps {
  adKey: string;
  className?: string;
}

/**
 * 原生横幅广告组件
 * 特点：4:1 宽高比，完全自适应容器宽度，不限制高度
 */
export function NativeBannerAd({ adKey, className = "" }: NativeBannerAdProps) {
  const { ref: containerRef, isActive } = useDeferredAdSlot<HTMLDivElement>({
    enabled: Boolean(adKey && adKey !== "0"),
    delayMs: 600,
  });
  const scriptLoadedRef = useRef(false);

  useEffect(() => {
    if (
      !adKey ||
      adKey === "0" ||
      !isActive ||
      scriptLoadedRef.current ||
      !containerRef.current
    )
      return;

    const container = containerRef.current;

    const script = document.createElement("script");
    script.async = true;
    script.setAttribute("data-cfasync", "false");
    script.src = `https://pl28666083.effectivegatecpm.com/${adKey}/invoke.js`;

    container.appendChild(script);
    scriptLoadedRef.current = true;

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
      scriptLoadedRef.current = false;
    };
  }, [adKey, containerRef, isActive]);

  if (!adKey || adKey === "0") return null;

  return (
    <div className={`w-full flex justify-center my-8 ${className}`}>
      <div className="w-full max-w-4xl">
        <div
          ref={containerRef}
          className="min-h-[120px] overflow-hidden rounded-2xl"
        >
          <div id={`container-${adKey}`} />
        </div>
      </div>
    </div>
  );
}

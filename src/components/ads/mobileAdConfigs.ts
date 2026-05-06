export type BannerAdType =
  | "banner-300x250"
  | "banner-468x60"
  | "banner-728x90"
  | "banner-160x600"
  | "banner-320x50";

export const AD_CONFIGS: Record<
  BannerAdType,
  {
    width: number;
    height: number;
  }
> = {
  "banner-300x250": {
    width: 300,
    height: 250,
  },
  "banner-468x60": {
    width: 468,
    height: 60,
  },
  "banner-728x90": {
    width: 728,
    height: 90,
  },
  "banner-160x600": {
    width: 160,
    height: 600,
  },
  "banner-320x50": {
    width: 320,
    height: 50,
  },
};

export interface MobileAdSelection {
  type: BannerAdType;
  adKey: string;
}

function isEnabledAdKey(adKey?: string): adKey is string {
  return Boolean(adKey && adKey !== "0");
}

function pickFirstEnabled(
  candidates: Array<MobileAdSelection | null>,
): MobileAdSelection | null {
  return (
    candidates.find(
      (candidate): candidate is MobileAdSelection =>
        Boolean(candidate && isEnabledAdKey(candidate.adKey)),
    ) ?? null
  );
}

export function getPreferredMobileBannerSelection(): MobileAdSelection | null {
  return pickFirstEnabled([
    {
      type: "banner-320x50",
      adKey: process.env.NEXT_PUBLIC_AD_MOBILE_320X50 || "",
    },
    {
      type: "banner-300x250",
      adKey: process.env.NEXT_PUBLIC_AD_BANNER_300X250 || "",
    },
  ]);
}

export function getPreferredMobileContentSelection(): MobileAdSelection | null {
  return pickFirstEnabled([
    {
      type: "banner-300x250",
      adKey: process.env.NEXT_PUBLIC_AD_BANNER_300X250 || "",
    },
    {
      type: "banner-320x50",
      adKey: process.env.NEXT_PUBLIC_AD_MOBILE_320X50 || "",
    },
  ]);
}

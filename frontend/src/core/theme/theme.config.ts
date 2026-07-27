export interface ThemePreset {
  id: "rpex-brand";
  label: string;
  brandHex: string;
  radius: string;
}

export const activeThemePreset: ThemePreset = {
  id: "rpex-brand",
  label: "RPEX Brand",
  brandHex: "#3e2154",
  radius: "0.75rem"
};

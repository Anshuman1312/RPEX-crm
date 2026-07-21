import { MouseEventHandler } from "react";

export interface QuickActionProps {
  label: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  color?: string;
  textColor?: string;
  isActive?: boolean;
}

export const QuickAction = ({
  label,
  onClick,
  color = "bg-slate-800/50",
  textColor = "text-slate-300",
  isActive = false,
}: QuickActionProps) => {
  const activeClasses = isActive
    ? "bg-cyan-500 text-slate-950 border-cyan-400 shadow-lg shadow-cyan-500/30 scale-[1.02]"
    : `${color} ${textColor} border-slate-700/60 hover:border-cyan-500 hover:shadow-cyan-500/10 hover:shadow-lg`;

  return (
    <button
      onClick={onClick}
      className={`border transition-all duration-200 p-4 rounded-2xl text-center group flex flex-col items-center justify-center min-h-[100px] active:scale-95 cursor-pointer ${activeClasses}`}
    >
      <p
        className={`text-sm font-bold group-hover:scale-105 transition-transform ${
          isActive ? "text-slate-950 font-extrabold" : ""
        }`}
      >
        {label}
      </p>
    </button>
  );
};

export default QuickAction;

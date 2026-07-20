export interface ComingSoonModalProps {
  isOpen: boolean;
  onClose: () => void;
  featureName?: string;
}

export const ComingSoonModal = ({
  isOpen,
  onClose,
  featureName = "This Feature",
}: ComingSoonModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full text-center shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
        <div className="w-14 h-14 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold">
          🚀
        </div>

        <div>
          <h3 className="text-xl font-bold text-white tracking-tight">
            {featureName} Coming Soon
          </h3>
          <p className="text-slate-400 text-xs mt-2 leading-relaxed">
            The <span className="text-cyan-400 font-bold">{featureName}</span> module is currently under active development and will be integrated in the upcoming release.
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-full py-3 px-4 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl transition-colors shadow-lg shadow-cyan-500/20 text-sm"
        >
          Got It
        </button>
      </div>
    </div>
  );
};

export default ComingSoonModal;

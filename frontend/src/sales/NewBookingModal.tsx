import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createBooking, fetchAvailablePlots } from "../services/crm";

type NewBookingModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function NewBookingModal({
  isOpen,
  onClose,
}: NewBookingModalProps) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(1);

  const [formData, setFormData] = useState({
    customer_name: "",
    phone: "",
    plot_id: "",
    plot_type: "Classic Plot",
    booking_amount: "",
    payment_plan: "Standard",
    notes: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: plots } = useQuery({
    queryKey: ["available-plots"],
    queryFn: fetchAvailablePlots,
    enabled: isOpen,
  });

  const mutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      alert("Booking Created Successfully!");
      handleClose();
    },
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.customer_name.trim()) {
      newErrors.customer_name = "Customer name is required";
    }
    if (!formData.phone.trim()) {
      newErrors.phone = "Mobile number is required";
    }
    if (!formData.plot_id) {
      newErrors.plot_id = "Please select an available plot";
    }
    if (!formData.booking_amount) {
      newErrors.booking_amount = "Booking amount is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      mutation.mutate(formData);
    }
  };

  const handleClose = () => {
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 md:p-6">
      <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in duration-200 border border-slate-100">
        {/* Header */}
        <div className="bg-slate-900 p-6 md:p-8 text-white flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-display font-bold tracking-tight">
              New Property Booking
            </h2>
            <p className="text-slate-400 text-sm mt-1">
              Sanskruti City Plotting Project
            </p>
          </div>
          <button
            onClick={handleClose}
            className="hover:rotate-90 transition-transform p-2.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white"
          >
            <svg
              width="24"
              height="24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form
          className="p-6 md:p-10 space-y-6"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Customer Section */}
            <div className="space-y-4">
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Customer Name
                </span>
                <input
                  className={`mt-1.5 w-full px-4 py-3.5 text-sm font-medium text-slate-900 bg-white rounded-xl border ${errors.customer_name ? "border-rose-500 focus:ring-rose-500 focus:border-rose-500" : "border-slate-200 focus:ring-cyan-500 focus:border-cyan-500"} focus:ring-2 transition-all outline-none`}
                  placeholder="Full Name"
                  value={formData.customer_name}
                  onChange={(e) =>
                    handleChange("customer_name", e.target.value)
                  }
                />
                {errors.customer_name && (
                  <span className="text-xs text-rose-500 font-semibold mt-1 block">
                    {errors.customer_name}
                  </span>
                )}
              </label>
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Mobile Number
                </span>
                <input
                  className={`mt-1.5 w-full px-4 py-3.5 text-sm font-medium text-slate-900 bg-white rounded-xl border ${errors.phone ? "border-rose-500 focus:ring-rose-500 focus:border-rose-500" : "border-slate-200 focus:ring-cyan-500 focus:border-cyan-500"} focus:ring-2 transition-all outline-none`}
                  placeholder="+91"
                  value={formData.phone}
                  onChange={(e) => handleChange("phone", e.target.value)}
                />
                {errors.phone && (
                  <span className="text-xs text-rose-500 font-semibold mt-1 block">
                    {errors.phone}
                  </span>
                )}
              </label>
            </div>

            {/* Plot Section */}
            <div className="space-y-4">
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Select Plot Type
                </span>
                <select
                  className="mt-1.5 w-full px-4 py-3.5 text-sm font-medium text-slate-900 bg-white rounded-xl border border-slate-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all outline-none cursor-pointer"
                  value={formData.plot_type}
                  onChange={(e) => handleChange("plot_type", e.target.value)}
                >
                  <option className="text-slate-900 bg-white">
                    Signature Plot
                  </option>
                  <option className="text-slate-900 bg-white">
                    Prestige Plot
                  </option>
                  <option className="text-slate-900 bg-white">
                    Premium Plot
                  </option>
                  <option className="text-slate-900 bg-white">
                    Classic Plot
                  </option>
                </select>
              </label>
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Available Plot No.
                </span>
                <select
                  className={`mt-1.5 w-full px-4 py-3.5 text-sm font-medium text-slate-900 bg-white rounded-xl border ${errors.plot_id ? "border-rose-500 focus:ring-rose-500 focus:border-rose-500" : "border-slate-200 focus:ring-cyan-500 focus:border-cyan-500"} focus:ring-2 transition-all outline-none cursor-pointer`}
                  value={formData.plot_id}
                  onChange={(e) => handleChange("plot_id", e.target.value)}
                >
                  <option value="" className="text-slate-900 bg-white">
                    Select a plot
                  </option>
                  {plots?.map((plot: any) => (
                    <option
                      key={plot.id}
                      value={plot.id}
                      className="text-slate-900 bg-white"
                    >
                      Plot {plot.plot_no} - {plot.size} sqft
                    </option>
                  ))}
                </select>
                {errors.plot_id && (
                  <span className="text-xs text-rose-500 font-semibold mt-1 block">
                    {errors.plot_id}
                  </span>
                )}
              </label>
            </div>
          </div>

          <hr className="border-slate-100 my-2" />

          {/* Payment Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <label className="block">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Booking Amount (₹)
              </span>
              <input
                type="number"
                className={`mt-1.5 w-full px-4 py-3.5 text-sm font-bold text-cyan-600 bg-white rounded-xl border ${errors.booking_amount ? "border-rose-500 focus:ring-rose-500 focus:border-rose-500" : "border-slate-200 focus:ring-cyan-500 focus:border-cyan-500"} focus:ring-2 transition-all outline-none`}
                placeholder="Minimum 51,000"
                value={formData.booking_amount}
                onChange={(e) => handleChange("booking_amount", e.target.value)}
              />
              {errors.booking_amount && (
                <span className="text-xs text-rose-500 font-semibold mt-1 block">
                  {errors.booking_amount}
                </span>
              )}
            </label>
            <label className="block">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Payment Plan
              </span>
              <select
                className="mt-1.5 w-full px-4 py-3.5 text-sm font-medium text-slate-900 bg-white rounded-xl border border-slate-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all outline-none cursor-pointer"
                value={formData.payment_plan}
                onChange={(e) => handleChange("payment_plan", e.target.value)}
              >
                <option className="text-slate-900 bg-white">
                  Standard (20-80)
                </option>
                <option className="text-slate-900 bg-white">
                  Downpayment (10% Discount)
                </option>
                <option className="text-slate-900 bg-white">
                  Construction Linked
                </option>
                <option className="text-slate-900 bg-white">Custom Plan</option>
              </select>
            </label>
          </div>
          <div className="flex gap-4 pt-6">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-6 py-3.5 rounded-xl border border-slate-200 font-bold text-slate-600 hover:bg-slate-50 transition-colors text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 px-6 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-bold shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50 text-sm"
            >
              {mutation.isPending ? "Processing..." : "Confirm Booking"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

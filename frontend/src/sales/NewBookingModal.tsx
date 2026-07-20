import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createBooking, fetchAvailablePlots } from "../services/crm";

type NewBookingModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function NewBookingModal({ isOpen, onClose }: NewBookingModalProps) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(1);

  const [formData, setFormData] = useState({
    customer_name: "",
    phone: "",
    plot_id: "",
    plot_type: "Classic Plot",
    booking_amount: "",
    payment_plan: "Standard",
    notes: ""
  });

  const { data: plots } = useQuery({
    queryKey: ["available-plots"],
    queryFn: fetchAvailablePlots,
    enabled: isOpen
  });

  const mutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      alert("Booking Created Successfully!");
      onClose();
    }
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in duration-200">
        
        {/* Header */}
        <div className="bg-slate-900 p-6 text-white flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-display font-bold">New Property Booking</h2>
            <p className="text-slate-400 text-sm">Sanskruti City Plotting Project</p>
          </div>
          <button onClick={onClose} className="hover:rotate-90 transition-transform p-2">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <form className="p-8 space-y-6" onSubmit={(e) => { e.preventDefault(); mutation.mutate(formData); }}>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Customer Section */}
            <div className="space-y-4">
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Customer Name</span>
                <input 
                  className="mt-1 w-full rounded-xl border-slate-200 focus:ring-cyan-500 focus:border-cyan-500" 
                  placeholder="Full Name"
                  required
                  value={formData.customer_name}
                  onChange={e => setFormData({...formData, customer_name: e.target.value})}
                />
              </label>
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Mobile Number</span>
                <input 
                  className="mt-1 w-full rounded-xl border-slate-200" 
                  placeholder="+91" 
                  required
                  value={formData.phone}
                  onChange={e => setFormData({...formData, phone: e.target.value})}
                />
              </label>
            </div>

            {/* Plot Section */}
            <div className="space-y-4">
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Select Plot Type</span>
                <select 
                  className="mt-1 w-full rounded-xl border-slate-200"
                  value={formData.plot_type}
                  onChange={e => setFormData({...formData, plot_type: e.target.value})}
                >
                  <option>Signature Plot</option>
                  <option>Prestige Plot</option>
                  <option>Premium Plot</option>
                  <option>Classic Plot</option>
                </select>
              </label>
              <label className="block">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Available Plot No.</span>
                <select 
                   className="mt-1 w-full rounded-xl border-slate-200"
                   required
                   value={formData.plot_id}
                   onChange={e => setFormData({...formData, plot_id: e.target.value})}
                >
                  <option value="">Select a plot</option>
                  {plots?.map((plot: any) => (
                    <option key={plot.id} value={plot.id}>Plot {plot.plot_no} - {plot.size} sqft</option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Payment Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <label className="block">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Booking Amount (₹)</span>
              <input 
                type="number" 
                className="mt-1 w-full rounded-xl border-slate-200 font-bold text-cyan-600" 
                placeholder="Minimum 51,000"
                value={formData.booking_amount}
                onChange={e => setFormData({...formData, booking_amount: e.target.value})}
              />
            </label>
            <label className="block">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Payment Plan</span>
              <select 
                className="mt-1 w-full rounded-xl border-slate-200"
                value={formData.payment_plan}
                onChange={e => setFormData({...formData, payment_plan: e.target.value})}
              >
                <option>Standard (20-80)</option>
                <option>Downpayment (10% Discount)</option>
                <option>Construction Linked</option>
                <option>Custom Plan</option>
              </select>
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button 
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 rounded-xl border border-slate-200 font-bold text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white font-bold shadow-lg shadow-cyan-200 transition-all disabled:opacity-50"
            >
              {mutation.isPending ? "Processing..." : "Confirm Booking"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
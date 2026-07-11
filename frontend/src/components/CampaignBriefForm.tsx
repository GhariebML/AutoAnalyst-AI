import React from 'react';
import { useForm } from 'react-hook-form';
import type { CampaignBrief } from '../types';
import { campaignService } from '../services/api';
import { Sparkles } from 'lucide-react';

interface CampaignBriefFormProps {
  onSubmit: (taskId: string) => void;
  isLoading?: boolean;
}

export const CampaignBriefForm: React.FC<CampaignBriefFormProps> = ({ onSubmit, isLoading = false }) => {
  const { register, handleSubmit } = useForm<CampaignBrief>({
    defaultValues: {
      businessName: '',
      productName: '',
      productDescription: '',
      targetAudience: '',
      goals: [],
      budget: 0,
      duration: '1-week',
      tone: 'professional',
    },
  });

  const [submitError, setSubmitError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleFormSubmit = async (data: CampaignBrief) => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const response = await campaignService.submitCampaign(data);
      onSubmit(response.taskId);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Failed to submit campaign');
    } finally {
      setIsSubmitting(false);
    }
  };

  const labelClass = 'block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-[0.15em] mb-1.5';
  const inputClass = 'w-full bg-white dark:bg-[#161B22] border border-gray-200 dark:border-gray-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600';

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Campaign Brief</h2>
        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5">Define mission parameters for AI orchestration.</p>
      </div>

      {submitError && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/40 rounded-lg text-red-300 text-xs flex gap-2">
          <span>⚠️</span>
          <span>{submitError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">

        {/* Business + Product — stacked */}
        <div>
          <label className={labelClass}>Business Name</label>
          <input
            type="text"
            {...register('businessName', { required: 'Required' })}
            className={inputClass}
            placeholder="e.g. FutureCorp"
          />
        </div>

        <div>
          <label className={labelClass}>Product / Service</label>
          <input
            type="text"
            {...register('productName', { required: 'Required' })}
            className={inputClass}
            placeholder="e.g. NeuralLink v2"
          />
        </div>

        <div>
          <label className={labelClass}>Description</label>
          <textarea
            {...register('productDescription', { required: 'Required' })}
            className={`${inputClass} h-20 resize-none`}
            placeholder="Value proposition & key features..."
          />
        </div>

        <div>
          <label className={labelClass}>Target Audience</label>
          <input
            type="text"
            {...register('targetAudience', { required: 'Required' })}
            className={inputClass}
            placeholder="e.g. Tech enthusiasts, early adopters"
          />
        </div>

        {/* Goals — compact chips */}
        <div>
          <label className={labelClass}>Campaign Goals</label>
          <div className="flex flex-wrap gap-2">
            {['Brand Awareness', 'Lead Gen', 'Sales', 'Engagement', 'Traffic'].map((goal) => (
              <label key={goal} className="cursor-pointer">
                <input type="checkbox" value={goal} {...register('goals')} className="sr-only peer" />
                <div className="bg-gray-50 dark:bg-[#161B22] border border-gray-100 dark:border-gray-800 rounded-lg px-3 py-1.5 text-[11px] font-medium text-slate-700 dark:text-slate-300 peer-checked:bg-primary/10 peer-checked:border-primary peer-checked:text-primary transition-all hover:bg-gray-100 dark:hover:bg-gray-800">
                  {goal}
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Budget + Duration — side by side */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Budget ($)</label>
            <input
              type="number"
              {...register('budget', { required: true, min: 1 })}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Timeline</label>
            <select
              {...register('duration', { required: true })}
              className={`${inputClass} cursor-pointer`}
            >
              <option value="1-week">1 Week</option>
              <option value="2-weeks">2 Weeks</option>
              <option value="1-month">1 Month</option>
              <option value="3-months">3 Months</option>
            </select>
          </div>
        </div>

        {/* Tone — 2 columns */}
        <div>
          <label className={labelClass}>Brand Persona</label>
          <div className="grid grid-cols-2 gap-2">
            {['Professional', 'Casual', 'Playful', 'Luxury', 'Technical', 'Modern & Edgy'].map((t) => (
              <label key={t} className="cursor-pointer">
                <input type="radio" value={t.toLowerCase()} {...register('tone')} className="sr-only peer" />
                <div className="bg-gray-50 dark:bg-[#161B22] border border-gray-100 dark:border-gray-800 rounded-lg py-2 text-[10px] font-bold text-center text-slate-700 dark:text-slate-300 peer-checked:bg-primary/10 peer-checked:border-primary peer-checked:text-primary transition-all hover:bg-gray-100 dark:hover:bg-gray-800 uppercase tracking-tight">
                  {t}
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isSubmitting || isLoading}
          className="w-full mt-2 bg-primary hover:bg-blue-600 disabled:bg-primary/40 disabled:text-slate-400 text-white font-bold py-3 rounded-xl transition-all hover:scale-[1.01] active:scale-95 flex items-center justify-center gap-2 group"
        >
          {isSubmitting || isLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Sparkles size={16} className="group-hover:rotate-12 transition-transform" />
          )}
          <span className="text-xs uppercase tracking-[0.2em]">Initialize Campaign Generation</span>
        </button>
      </form>
    </div>
  );
};

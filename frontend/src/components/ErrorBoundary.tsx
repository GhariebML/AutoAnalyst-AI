import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-[var(--bg-main)] p-8">
          <div className="max-w-md w-full glass-panel p-8 text-center border border-red-500/20 shadow-2xl shadow-red-500/10">
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-6">
              <AlertTriangle className="text-red-500" size={32} />
            </div>
            <h2 className="text-xl font-bold text-[var(--text-main)] mb-2">System Failure</h2>
            <p className="text-sm text-[var(--text-muted)] mb-6">
              The dashboard encountered an unexpected error. Our engineers have been notified.
            </p>
            <div className="bg-red-500/5 border border-red-500/10 rounded-lg p-4 text-left mb-8 overflow-x-auto">
              <code className="text-xs text-red-400 font-mono">
                {this.state.error?.message || 'Unknown error'}
              </code>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[var(--bg-card)] hover:bg-slate-800 border border-[var(--border-main)] rounded-xl transition-colors font-bold text-sm text-[var(--text-main)]"
            >
              <RefreshCcw size={16} />
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

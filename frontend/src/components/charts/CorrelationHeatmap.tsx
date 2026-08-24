import React, { useState } from 'react';
import { Sparkles, Filter } from 'lucide-react';

interface CorrelationHeatmapProps {
  matrix: Record<string, Record<string, number>>;
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({ matrix }) => {
  const columns = Object.keys(matrix || {});
  const [hoveredCell, setHoveredCell] = useState<{ row: string; col: string; val: number } | null>(null);
  const [threshold, setThreshold] = useState<number>(0.0);

  if (columns.length === 0) {
    return (
      <div className="p-6 text-center text-slate-400 text-sm italic glass-card rounded-xl">
        No correlation matrix data available.
      </div>
    );
  }

  // Get color for correlation value (-1 to +1)
  const getCellColor = (val: number) => {
    if (Math.abs(val) < threshold) return 'rgba(30, 41, 59, 0.4)';
    if (val >= 0) {
      // Blue/Cyan to Purple for positive
      const opacity = Math.min(Math.max(val, 0.15), 0.95);
      return `rgba(99, 102, 241, ${opacity})`;
    } else {
      // Rose/Red for negative
      const opacity = Math.min(Math.max(Math.abs(val), 0.15), 0.95);
      return `rgba(244, 63, 94, ${opacity})`;
    }
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">Interactive Correlation Matrix</h4>
            <p className="text-xs text-slate-400">Hover over cells to inspect pairwise Pearson & Spearman coefficients</p>
          </div>
        </div>

        {/* Filter threshold */}
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Filter className="w-3.5 h-3.5 text-cyan-400" />
          <span>Min Strength:</span>
          <span className="font-mono font-bold text-cyan-300">{threshold.toFixed(2)}</span>
          <input
            type="range"
            min="0"
            max="0.8"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-20 accent-indigo-500 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
          />
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full align-middle">
          <div className="grid gap-1.5" style={{ gridTemplateColumns: `auto repeat(${columns.length}, minmax(42px, 1fr))` }}>
            {/* Header row */}
            <div className="h-9"></div>
            {columns.map((col) => (
              <div
                key={`header-${col}`}
                className="h-9 px-1 text-[11px] font-mono text-slate-400 font-semibold truncate text-center flex items-center justify-center -rotate-45 sm:rotate-0"
                title={col}
              >
                {col.length > 7 ? `${col.slice(0, 6)}…` : col}
              </div>
            ))}

            {/* Matrix rows */}
            {columns.map((row) => (
              <React.Fragment key={`row-frag-${row}`}>
                <div
                  className="px-2 py-1.5 text-xs font-mono text-slate-300 font-medium truncate flex items-center justify-end pr-3"
                  title={row}
                >
                  {row.length > 10 ? `${row.slice(0, 9)}…` : row}
                </div>
                {columns.map((col) => {
                  const val = matrix[row]?.[col] ?? 0;
                  const isHovered = hoveredCell?.row === row && hoveredCell?.col === col;
                  return (
                    <div
                      key={`cell-${row}-${col}`}
                      onMouseEnter={() => setHoveredCell({ row, col, val })}
                      onMouseLeave={() => setHoveredCell(null)}
                      className={`relative h-10 rounded-lg flex items-center justify-center transition-all duration-200 cursor-pointer text-[11px] font-mono font-bold ${
                        isHovered ? 'scale-110 z-10 ring-2 ring-cyan-400 shadow-glow-cyan' : ''
                      }`}
                      style={{ backgroundColor: getCellColor(val) }}
                    >
                      <span className={Math.abs(val) > 0.4 ? 'text-white' : 'text-slate-300'}>
                        {val.toFixed(2)}
                      </span>
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Hover Info Tooltip Bar */}
      <div className="h-8 flex items-center justify-between text-xs px-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
        {hoveredCell ? (
          <div className="flex items-center gap-3">
            <span className="text-slate-400">Pair:</span>
            <span className="font-mono text-white font-semibold">
              {hoveredCell.row} ⟷ {hoveredCell.col}
            </span>
            <span className="text-slate-400">| Correlation:</span>
            <span
              className={`font-mono font-bold ${
                hoveredCell.val > 0 ? 'text-indigo-400' : hoveredCell.val < 0 ? 'text-rose-400' : 'text-slate-400'
              }`}
            >
              {hoveredCell.val > 0 ? '+' : ''}
              {hoveredCell.val.toFixed(4)}
            </span>
            <span className="text-[11px] text-slate-500">
              ({Math.abs(hoveredCell.val) > 0.7 ? 'Strong' : Math.abs(hoveredCell.val) > 0.3 ? 'Moderate' : 'Weak'})
            </span>
          </div>
        ) : (
          <span className="text-slate-500 italic">Hover over any cell to see pairwise interaction details.</span>
        )}

        {/* Legend */}
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-500"></span>
            <span>-1.0 (Neg)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-slate-700"></span>
            <span>0.0</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-indigo-500"></span>
            <span>+1.0 (Pos)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

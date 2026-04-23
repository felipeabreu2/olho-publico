"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatBRLCompact } from "@olho/shared";
import { chartTheme } from "./_theme";

export interface DonutDatum {
  label: string;
  value: number;
}

interface Props {
  data: DonutDatum[];
  height?: number;
  showLegend?: boolean;
}

export function DonutChart({ data, height = 220, showLegend = true }: Props) {
  if (data.length === 0) return null;

  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="space-y-3">
      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="50%"
              innerRadius="55%"
              outerRadius="85%"
              paddingAngle={2}
              stroke="none"
            >
              {data.map((_, i) => (
                <Cell
                  key={i}
                  fill={chartTheme.colors.palette[i % chartTheme.colors.palette.length]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: chartTheme.colors.tooltipBg,
                border: `1px solid ${chartTheme.colors.tooltipBorder}`,
                borderRadius: 6,
                fontSize: 12,
              }}
              labelStyle={{ color: chartTheme.colors.primary }}
              itemStyle={{ color: chartTheme.colors.primary }}
              formatter={(value: number) => [formatBRLCompact(value), "Valor"]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      {showLegend && (
        <ul className="space-y-1.5 text-sm">
          {data.map((d, i) => {
            const pct = total > 0 ? ((d.value / total) * 100).toFixed(1) : "0";
            return (
              <li key={d.label} className="flex items-center gap-2">
                <span
                  className="size-3 rounded-sm shrink-0"
                  style={{
                    background: chartTheme.colors.palette[i % chartTheme.colors.palette.length],
                  }}
                />
                <span className="flex-1 truncate text-fg-muted">{d.label}</span>
                <span className="font-mono text-xs text-fg-subtle">{pct}%</span>
                <span className="font-mono text-fg">{formatBRLCompact(d.value)}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

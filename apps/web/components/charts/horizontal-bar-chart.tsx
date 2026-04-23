"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatBRLCompact } from "@olho/shared";
import { chartTheme } from "./_theme";

export interface BarDatum {
  label: string;
  value: number;
}

interface Props {
  data: BarDatum[];
  height?: number;
  color?: string;
}

export function HorizontalBarChart({
  data,
  height = 280,
  color = chartTheme.colors.accent.fact,
}: Props) {
  if (data.length === 0) return null;

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 8, right: 24, bottom: 0, left: 8 }}
        >
          <CartesianGrid stroke={chartTheme.colors.grid} strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            stroke={chartTheme.colors.axis}
            tick={{ fontSize: chartTheme.font.sizeAxis, fill: chartTheme.colors.axis }}
            tickFormatter={(v) => formatBRLCompact(v)}
          />
          <YAxis
            type="category"
            dataKey="label"
            stroke={chartTheme.colors.axis}
            tick={{ fontSize: chartTheme.font.sizeAxis, fill: chartTheme.colors.axis }}
            width={140}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.04)" }}
            contentStyle={{
              background: chartTheme.colors.tooltipBg,
              border: `1px solid ${chartTheme.colors.tooltipBorder}`,
              borderRadius: 6,
              fontSize: 12,
            }}
            formatter={(value: number) => [formatBRLCompact(value), "Valor"]}
          />
          <Bar dataKey="value" fill={color} radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

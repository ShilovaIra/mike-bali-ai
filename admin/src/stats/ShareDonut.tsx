import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { DonutSlice } from './buildDonutSlices'

const SERIES = ['#4b764b', '#397094', '#8d5570', '#3a653b', '#215271']
const OTHER_COLOR = '#44484c'

type ShareDonutProps = {
  slices: DonutSlice[]
}

function sliceColor(slice: DonutSlice, index: number): string {
  if (slice.key === 'other') return OTHER_COLOR
  return SERIES[index % SERIES.length]!
}

function ShareTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: Array<{ payload: DonutSlice }>
}) {
  if (!active || !payload?.[0]) return null
  const slice = payload[0].payload
  return (
    <div className="tip">
      {slice.label}: {slice.value}
    </div>
  )
}

export function ShareDonut({ slices }: ShareDonutProps) {
  if (slices.length === 0) {
    return <p className="quiet">Пока нет данных</p>
  }

  const colored = slices.map((slice, index) => ({
    ...slice,
    fill: sliceColor(slice, index),
  }))

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center">
      <div className="h-44 w-44 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={colored}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="50%"
              innerRadius="58%"
              outerRadius="88%"
              paddingAngle={1}
              stroke="#fafbfc"
              strokeWidth={1}
            >
              {colored.map((slice) => (
                <Cell key={slice.key} fill={slice.fill} />
              ))}
            </Pie>
            <Tooltip content={<ShareTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="legend">
        {colored.map((slice) => (
          <li key={slice.key}>
            <span className="legend-label">
              <span className="swatch" style={{ backgroundColor: slice.fill }} aria-hidden />
              <span>{slice.label}</span>
            </span>
            <span className="legend-num">{slice.percent}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

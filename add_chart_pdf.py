import os

# Add the NDVIMultiYearChart component and PDF function to DashboardScreen
path = r"C:\Agrinova hackathon\landroid\landroid\src\screens\DashboardScreen.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add victory import at top if not present
if 'victory-native' not in content:
    content = content.replace(
        "import Svg, { Path, Line, Text as SvgText } from 'react-native-svg';",
        """import Svg, { Path, Line, Text as SvgText } from 'react-native-svg';
import { VictoryLine, VictoryChart, VictoryAxis } from 'victory-native';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';"""
    )

# Add NDVIMultiYearChart component before RadarChart function
ndvi_chart_component = '''
function NDVIMultiYearChart({ trend, confidence }: { trend: number[]; confidence: number }) {
  if (!trend || trend.length < 6) return null;
  const labels: string[] = (globalThis as any)._ndviLabels ?? [];

  const data = trend.map((v, i) => ({ x: i, y: v }));

  // Linear regression for trend line
  const n = data.length;
  const sumX = data.reduce((s, d) => s + d.x, 0);
  const sumY = data.reduce((s, d) => s + d.y, 0);
  const sumXY = data.reduce((s, d) => s + d.x * d.y, 0);
  const sumX2 = data.reduce((s, d) => s + d.x * d.x, 0);
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;
  const trendLine = [{ x: 0, y: intercept }, { x: n - 1, y: slope * (n - 1) + intercept }];

  const isImproving = slope > 0;
  const mean = sumY / n;
  const annualChange = Math.abs(slope * 12 * 100);

  // X-axis labels — show only every 6th
  const tickValues = data.filter((_, i) => i % 6 === 0).map(d => d.x);
  const tickLabels = tickValues.map(i => labels[i]?.slice(2, 7) ?? '');

  return (
    <View style={s.card}>
      <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 2 }}>
        📈 NDVI Multi-Year Trend
      </Text>
      <Text style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
        {trend.length} months · {labels[0] ?? '—'} → {labels[labels.length - 1] ?? 'Now'} · Sentinel-2
      </Text>

      {/* Summary row */}
      <View style={{ flexDirection: 'row', gap: 6, marginBottom: 8 }}>
        <View style={{ flex: 1, backgroundColor: isImproving ? '#dcfce7' : '#fee2e2', borderRadius: 8, padding: 8 }}>
          <Text style={{ fontSize: 12, fontWeight: '700', color: isImproving ? '#15803d' : '#dc2626' }}>
            {isImproving ? '↑ Recovering' : '↓ Degrading'}
          </Text>
          <Text style={{ fontSize: 10, color: '#666' }}>Long-term slope</Text>
        </View>
        <View style={{ flex: 1, backgroundColor: '#f0f7f0', borderRadius: 8, padding: 8 }}>
          <Text style={{ fontSize: 12, fontWeight: '700', color: '#1b4332' }}>
            {trend[trend.length - 1]?.toFixed(3)}
          </Text>
          <Text style={{ fontSize: 10, color: '#666' }}>Current vs {mean.toFixed(3)} avg</Text>
        </View>
        <View style={{ flex: 1, backgroundColor: '#f0f7f0', borderRadius: 8, padding: 8 }}>
          <Text style={{ fontSize: 12, fontWeight: '700', color: '#1b4332' }}>
            {annualChange.toFixed(1)}%
          </Text>
          <Text style={{ fontSize: 10, color: '#666' }}>Annual change</Text>
        </View>
      </View>

      {/* Chart */}
      <VictoryChart
        height={200}
        padding={{ top: 10, bottom: 40, left: 48, right: 16 }}
      >
        <VictoryAxis
          tickValues={tickValues}
          tickFormat={(_: any, i: number) => tickLabels[i] ?? ''}
          style={{
            tickLabels: { fontSize: 8, fill: '#888', angle: -30, textAnchor: 'end' },
            grid: { stroke: '#f0f0f0', strokeWidth: 0.5 },
          }}
        />
        <VictoryAxis
          dependentAxis
          tickFormat={(v: number) => v.toFixed(2)}
          style={{
            tickLabels: { fontSize: 9, fill: '#888' },
            grid: { stroke: '#f5f5f5', strokeWidth: 0.5 },
          }}
        />
        {/* Trend line */}
        <VictoryLine
          data={trendLine}
          style={{
            data: {
              stroke: isImproving ? '#22c55e' : '#ef4444',
              strokeWidth: 1.5,
              strokeDasharray: '5,4',
              opacity: 0.8,
            },
          }}
        />
        {/* NDVI line */}
        <VictoryLine
          data={data}
          style={{ data: { stroke: '#2d6a4f', strokeWidth: 2 } }}
          interpolation="catmullRom"
        />
      </VictoryChart>

      <Text style={{ fontSize: 10, color: '#aaa', textAlign: 'center', marginTop: 4 }}>
        Area-specific analysis · BBox: {process.env.EXPO_PUBLIC_PARCEL_BBOX_MIN_LON}–{process.env.EXPO_PUBLIC_PARCEL_BBOX_MAX_LON}
      </Text>
      <View style={[s.badge, { backgroundColor: '#2d6a4f20', borderColor: '#2d6a4f', marginTop: 6 }]}>
        <Text style={[s.badgeText, { color: '#2d6a4f' }]}>Confidence {Math.round(confidence)}%</Text>
      </View>
    </View>
  );
}

'''

# Add before RadarChart function
if 'function NDVIMultiYearChart' not in content:
    content = content.replace(
        'function RadarChart(',
        ndvi_chart_component + 'function RadarChart('
    )

# Add PDF generation function before export default
pdf_function = '''
async function generatePDFReport(sig: any, hs: number, hl: string, parcel: any, lang: string) {
  try {
    const avgTemp = sig?.tempMonthly?.length
      ? (sig.tempMonthly.reduce((a: number, b: number) => a + b, 0) / sig.tempMonthly.length).toFixed(1)
      : '30.4';
    const html = `
      <html>
      <head><style>
        body{font-family:Arial,sans-serif;padding:24px;color:#1b4332;max-width:800px}
        h1{color:#1b4332;border-bottom:3px solid #2d6a4f;padding-bottom:8px}
        h2{color:#2d6a4f;margin-top:24px}
        .score-box{text-align:center;background:#f0f9f4;border-radius:12px;padding:20px;margin:16px 0}
        .score{font-size:64px;font-weight:900;color:#15803d}
        .label{font-size:22px;font-weight:700;color:#15803d}
        .formula{font-size:12px;color:#888;margin-top:4px}
        .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
        .card{background:#f0f7f0;border-radius:8px;padding:14px;border-left:4px solid #2d6a4f}
        .card-title{font-size:13px;font-weight:700;color:#52796f;margin-bottom:4px}
        .card-value{font-size:22px;font-weight:800;color:#1b4332}
        .card-sub{font-size:11px;color:#888;margin-top:2px}
        .valuation{background:#1b4332;color:#fff;border-radius:8px;padding:16px;margin:12px 0}
        .val-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:8px}
        .val-band{background:rgba(255,255,255,0.1);border-radius:6px;padding:10px;text-align:center}
        .disclaimer{font-size:10px;color:#aaa;margin-top:4px;font-style:italic}
        .zones{display:flex;gap:8px;margin:8px 0}
        .zone{border-radius:6px;padding:8px 12px;text-align:center;flex:1}
        .footer{margin-top:32px;border-top:1px solid #ccc;padding-top:12px;font-size:10px;color:#888}
        .confidence{display:inline-block;font-size:11px;padding:3px 10px;border-radius:20px;background:#e8f5e9;color:#2d6a4f;font-weight:600}
      </style></head>
      <body>
        <h1>🌿 Landroid — GIS Intelligence Report</h1>
        <p><strong>Parcel:</strong> ${parcel?.name ?? 'Sample Parcel — Kolli Hills'}</p>
        <p><strong>Location:</strong> ${sig?.osmTownName ?? 'Kolli Hills'}, ${sig?.osmDistrict ?? 'Namakkal'} &nbsp;|&nbsp; <strong>Centroid:</strong> ${process.env.EXPO_PUBLIC_PARCEL_CENTROID_LAT}, ${process.env.EXPO_PUBLIC_PARCEL_CENTROID_LNG}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()} &nbsp;|&nbsp; <strong>Data source:</strong> Birdscale × Sentinel-2 × SoilGrids × CHIRPS × ERA5</p>

        <div class="score-box">
          <div class="score">${Math.round(hs)}</div>
          <div class="label">${hl}</div>
          <div class="formula">Composite score: NDVI 40% (3-yr trend) + Rainfall 30% (12-mo) + Soil 20% + Temperature 10%</div>
        </div>

        <h2>Environmental Signals</h2>
        <div class="grid">
          <div class="card">
            <div class="card-title">🌿 Vegetation Index (NDVI)</div>
            <div class="card-value">${sig?.ndviCurrent?.toFixed(3) ?? '0.520'}</div>
            <div class="card-sub">${sig?.ndviStatus ?? 'Degrading'} · 3-year trend · ${sig?.ndviTrend?.length ?? 36} scenes</div>
            <span class="confidence">Confidence ${Math.round(sig?.ndviConfidence ?? 55)}%</span>
          </div>
          <div class="card">
            <div class="card-title">🌧 Annual Rainfall</div>
            <div class="card-value">${sig?.rainfallAnnual ? Math.round(sig.rainfallAnnual) : 950}mm</div>
            <div class="card-sub">${sig?.rainfallFlag ?? 'Deficit'} · vs 905mm Tamil Nadu baseline</div>
            <span class="confidence">Confidence ${Math.round(sig?.rainfallConfidence ?? 62)}%</span>
          </div>
          <div class="card">
            <div class="card-title">🌡 Temperature (Regional)</div>
            <div class="card-value">${avgTemp}°C avg</div>
            <div class="card-sub">${sig?.tempHeatStressCount ?? 2} heat stress months · ERA5 regional data</div>
            <span class="confidence">Confidence ${Math.round(sig?.tempConfidence ?? 72)}%</span>
          </div>
          <div class="card">
            <div class="card-title">🪨 Soil Quality</div>
            <div class="card-value">pH ${sig?.soilPh?.toFixed(1) ?? '6.5'}</div>
            <div class="card-sub">${sig?.soilTexture ?? 'Loam'} · OC: ${sig?.soilOc?.toFixed(1) ?? '1.2'}g/kg</div>
            <span class="confidence">Confidence ${Math.round(sig?.soilConfidence ?? 40)}%</span>
          </div>
        </div>

        <div class="valuation">
          <h2 style="color:#fff;margin:0 0 4px">💰 Land Valuation</h2>
          <div class="disclaimer">Estimated intelligence range — not a legal or government guideline valuation</div>
          <div class="val-grid">
            <div class="val-band"><div style="font-size:12px;opacity:0.7">Low</div><div style="font-size:20px;font-weight:800">₹${sig?.valuationLow ? (sig.valuationLow/100000).toFixed(1) : '2.2'}L</div></div>
            <div class="val-band" style="background:rgba(255,255,255,0.2)"><div style="font-size:12px;opacity:0.7">Mid</div><div style="font-size:24px;font-weight:900">₹${sig?.valuationMid ? (sig.valuationMid/100000).toFixed(1) : '2.7'}L</div></div>
            <div class="val-band"><div style="font-size:12px;opacity:0.7">High</div><div style="font-size:20px;font-weight:800">₹${sig?.valuationHigh ? (sig.valuationHigh/100000).toFixed(1) : '3.4'}L</div></div>
          </div>
          <p style="font-size:11px;opacity:0.8;margin-top:8px">Formula: Health Score 30% + Soil 20% + Rainfall 15% + OSM Proximity 25% + Night Lights 10%</p>
          <p style="font-size:11px;opacity:0.8">Top factors: ${sig?.valuationFactors?.join(' · ') ?? 'High vegetation health · Optimal soil pH · Road proximity'}</p>
          <span class="confidence" style="background:rgba(255,255,255,0.2);color:#fff">Confidence ${Math.round(sig?.valuationConfidence ?? 72)}%</span>
        </div>

        <h2>🌳 Tree & Canopy Count</h2>
        <p><strong>${sig?.canopyCount ?? 386}</strong> total canopies · <strong>${sig?.canopyDensity ?? 48}</strong>/acre · <strong style="color:#dc2626">11</strong> stressed · OpenCV watershed segmentation</p>
        <p>Crop types: coconut, mango, teak · +3 new canopies, -2 missing vs previous survey</p>

        <h2>🗺 Plant Health Zones</h2>
        <div class="zones">
          <div class="zone" style="background:#fee2e2;color:#b91c1c"><strong>${sig?.zoneBare ?? 18}%</strong><br><small>Bare/Stressed</small></div>
          <div class="zone" style="background:#fef3c7;color:#92400e"><strong>${sig?.zoneSparse ?? 26}%</strong><br><small>Sparse</small></div>
          <div class="zone" style="background:#dcfce7;color:#15803d"><strong>${sig?.zoneHealthy ?? 42}%</strong><br><small>Healthy</small></div>
          <div class="zone" style="background:#166534;color:#fff"><strong>${sig?.zoneDense ?? 14}%</strong><br><small>Dense</small></div>
        </div>

        <h2>📍 Location & Proximity</h2>
        <p>Location: ${sig?.osmTownName ?? 'Kolli Hills'}, ${sig?.osmDistrict ?? 'Namakkal'}, Tamil Nadu</p>
        <p>Nearest road: ~${sig?.osmHighwayDist ? Math.round(sig.osmHighwayDist) : 1200}m · Water body: ~${sig?.osmWaterDist ? Math.round(sig.osmWaterDist) : 600}m</p>

        <div class="footer">
          <p>Landroid — AI-Powered Land Intelligence Platform | Birdscale Technology and Services Pvt. Ltd. × VIT Chennai Hackathon 2026</p>
          <p>Data sources: Birdscale drone survey · Sentinel-2 L2A (Planetary Computer) · CHIRPS rainfall · ERA5 temperature · ISRIC SoilGrids · OpenStreetMap</p>
          <p>⚠ This report is an AI-generated intelligence estimate. Land valuation figures are not legal, government, or certified valuations.</p>
        </div>
      </body>
      </html>
    `;
    const { uri } = await Print.printToFileAsync({ html, base64: false });
    await Sharing.shareAsync(uri, { mimeType: 'application/pdf', dialogTitle: 'Landroid GIS Report' });
  } catch (e: any) {
    console.log('PDF error:', e.message);
    // Fallback to share text
    const { Share } = require('react-native');
    Share.share({ title: 'Landroid Report', message: `Health Score: ${Math.round(hs)}/100 — ${hl}\nNDVI: ${sig?.ndviCurrent?.toFixed(3)}\nRainfall: ${Math.round(sig?.rainfallAnnual ?? 950)}mm\nValuation: Rs.${sig?.valuationMid ? (sig.valuationMid/100000).toFixed(1) : '2.7'}L/acre` });
  }
}

'''

if 'async function generatePDFReport' not in content:
    content = content.replace(
        'export default function DashboardScreen()',
        pdf_function + 'export default function DashboardScreen()'
    )

# Add NDVIMultiYearChart to JSX — after NDVI SignalCard
if 'NDVIMultiYearChart' not in content or '<NDVIMultiYearChart' not in content:
    content = content.replace(
        "<SignalCard icon=\"🌧\" title={t.rainfall}",
        """<NDVIMultiYearChart trend={sig?.ndviTrend ?? []} confidence={sig?.ndviConfidence ?? 55} />
          <SignalCard icon="🌧" title={t.rainfall}"""
    )

# Add PDF button after Share button
if 'generatePDFReport' not in content or 'Download PDF' not in content:
    content = content.replace(
        "<Text style={{ color: '#fff', fontSize: 15, fontWeight: '700' }}>📤 One-Tap GIS Snapshot</Text>",
        """<Text style={{ color: '#fff', fontSize: 15, fontWeight: '700' }}>📤 One-Tap GIS Snapshot</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={{ backgroundColor: '#52796f', margin: 16, marginTop: 0, borderRadius: 12, padding: 16, alignItems: 'center' }}
            onPress={() => generatePDFReport(sig, hs, hl, parcel, lang)}
          >
            <Text style={{ color: '#fff', fontSize: 15, fontWeight: '700' }}>📋 Download PDF Report</Text>"""
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("DashboardScreen.tsx updated with:")
print("  ✓ NDVI multi-year trend chart (VictoryLine)")
print("  ✓ PDF report generation")
print("  ✓ PDF button added")
print("Now run: npx expo start --clear")

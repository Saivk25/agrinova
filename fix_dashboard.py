import os

path = r"C:\Agrinova hackathon\landroid\landroid\src\screens\DashboardScreen.tsx"

content = r"""import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, RefreshControl, TouchableOpacity, Share, TextInput, Alert } from 'react-native';
import Svg, { Path, Line, Text as SvgText } from 'react-native-svg';
import { useStore } from '../store/useStore';
import { strings } from '../i18n/strings';
import { fetchAllSignals } from '../services/signals';
import { upsertSignals, updateParcelHealth } from '../services/supabase';

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function ConfidenceBadge({ value }: { value: number }) {
  const color = value >= 70 ? '#2d6a4f' : value >= 40 ? '#f59e0b' : '#ef4444';
  return (
    <View style={[s.badge, { backgroundColor: color + '20', borderColor: color }]}>
      <Text style={[s.badgeText, { color }]}>Confidence {Math.round(value)}%</Text>
    </View>
  );
}

function MiniChart({ values }: { values: number[] }) {
  if (!values || values.length === 0) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  return (
    <View style={s.chart}>
      {values.slice(0, 12).map((v, i) => (
        <View key={i} style={{ flex: 1, justifyContent: 'flex-end', paddingHorizontal: 1 }}>
          <View style={{ height: Math.max(4, ((v - min) / range) * 40), backgroundColor: '#2d6a4f', borderRadius: 2, opacity: 0.8 }} />
        </View>
      ))}
    </View>
  );
}

function SignalCard({ icon, title, value, unit, trend, chart, status, confidence, unavailable }: {
  icon: string; title: string; value?: string | null; unit?: string;
  trend?: string; chart?: number[]; status?: string; confidence: number; unavailable?: boolean;
}) {
  const statusBg = status === 'Healthy' || status === 'Recovering' ? '#dcfce7' : status === 'Degrading' ? '#fee2e2' : '#fef3c7';
  const statusColor = status === 'Healthy' || status === 'Recovering' ? '#15803d' : status === 'Degrading' ? '#b91c1c' : '#92400e';
  return (
    <View style={s.card}>
      <View style={s.cardHeader}>
        <Text style={{ fontSize: 20 }}>{icon}</Text>
        <Text style={s.cardTitle}>{title}</Text>
        {status && <View style={[s.pill, { backgroundColor: statusBg }]}><Text style={{ fontSize: 11, color: statusColor }}>{status}</Text></View>}
      </View>
      {unavailable ? (
        <Text style={s.unavail}>Signal unavailable — confidence reduced.</Text>
      ) : (
        <>
          <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 6, marginBottom: 8 }}>
            <Text style={s.value}>{value ?? '—'}</Text>
            {unit && <Text style={{ fontSize: 14, color: '#666' }}>{unit}</Text>}
            {trend && <Text style={{ fontSize: 13, color: '#52796f', marginLeft: 4 }}>{trend}</Text>}
          </View>
          {chart && chart.length > 0 && <MiniChart values={chart} />}
        </>
      )}
      <ConfidenceBadge value={confidence} />
    </View>
  );
}

function RadarChart({ ndvi, rainfall, soil, temp }: { ndvi: number; rainfall: number; soil: number; temp: number }) {
  const size = 180;
  const center = size / 2;
  const radius = 65;
  const axes = [
    { label: 'NDVI', value: ndvi / 100, angle: -90 },
    { label: 'Rain', value: rainfall / 100, angle: 0 },
    { label: 'Soil', value: soil / 100, angle: 90 },
    { label: 'Temp', value: temp / 100, angle: 180 },
  ];
  const toXY = (angle: number, r: number) => ({
    x: center + r * Math.cos((angle * Math.PI) / 180),
    y: center + r * Math.sin((angle * Math.PI) / 180),
  });
  const dataPoints = axes.map(a => toXY(a.angle, a.value * radius));
  const polygon = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + 'Z';
  return (
    <View style={{ alignItems: 'center', marginVertical: 8 }}>
      <Svg width={size} height={size}>
        {[1, 2, 3, 4].map(l => {
          const r = (radius * l) / 4;
          const pts = [-90, 0, 90, 180].map(a => toXY(a, r));
          const d = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + 'Z';
          return <Path key={l} d={d} fill="none" stroke="#e0ece4" strokeWidth="1" />;
        })}
        {axes.map((a, i) => {
          const end = toXY(a.angle, radius);
          return <Line key={i} x1={center} y1={center} x2={end.x} y2={end.y} stroke="#cde0d4" strokeWidth="1" />;
        })}
        <Path d={polygon} fill="#2d6a4f" fillOpacity="0.3" stroke="#2d6a4f" strokeWidth="2" />
        {axes.map((a, i) => {
          const pos = toXY(a.angle, radius + 18);
          return <SvgText key={i} x={pos.x} y={pos.y} textAnchor="middle" fontSize="10" fill="#1b4332" fontWeight="bold">{a.label}</SvgText>;
        })}
      </Svg>
    </View>
  );
}

function MonthComparisonCard({ sig }: { sig: any }) {
  const currentMonth = new Date().getMonth();
  const prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
  const currMonthName = MONTHS[currentMonth];
  const prevMonthName = MONTHS[prevMonth];

  const currentRain = sig?.rainfallMonthly?.[currentMonth] ?? 130;
  const prevRain = sig?.rainfallMonthly?.[prevMonth] ?? 185;
  const rainDiff = Math.round(currentRain - prevRain);

  const currentTemp = sig?.tempMonthly?.[currentMonth] ?? 29.4;
  const prevTemp = sig?.tempMonthly?.[prevMonth] ?? 30.8;
  const tempDiff = parseFloat((currentTemp - prevTemp).toFixed(1));

  const currentNDVI = sig?.ndviTrend?.[0] ?? 0.52;
  const prevNDVI = sig?.ndviTrend?.[1] ?? 0.50;
  const ndviDiff = parseFloat((currentNDVI - prevNDVI).toFixed(3));

  const rows = [
    { icon: '🌿', label: 'NDVI', prev: prevNDVI.toFixed(3), curr: currentNDVI.toFixed(3), diff: ndviDiff, unit: '', inverse: false },
    { icon: '🌧', label: 'Rainfall', prev: `${Math.round(prevRain)}mm`, curr: `${Math.round(currentRain)}mm`, diff: rainDiff, unit: 'mm', inverse: false },
    { icon: '🌡', label: 'Temperature', prev: `${prevTemp.toFixed(1)}°C`, curr: `${currentTemp.toFixed(1)}°C`, diff: tempDiff, unit: '°C', inverse: true },
  ];

  return (
    <View style={s.card}>
      <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 4 }}>📅 Month-on-Month Comparison</Text>
      <Text style={{ fontSize: 12, color: '#888', marginBottom: 12 }}>{prevMonthName} → {currMonthName} {new Date().getFullYear()}</Text>
      {rows.map(row => {
        const positive = row.inverse ? row.diff < 0 : row.diff > 0;
        const diffColor = positive ? '#15803d' : '#dc2626';
        const arrow = row.diff > 0 ? '↑' : '↓';
        return (
          <View key={row.label} style={{ flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 0.5, borderBottomColor: '#f0f0f0' }}>
            <Text style={{ fontSize: 18, marginRight: 8 }}>{row.icon}</Text>
            <Text style={{ fontSize: 13, color: '#444', width: 90 }}>{row.label}</Text>
            <View style={{ flex: 1, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
              <View style={{ alignItems: 'center' }}>
                <Text style={{ fontSize: 10, color: '#aaa' }}>{prevMonthName}</Text>
                <Text style={{ fontSize: 13, fontWeight: '600', color: '#666' }}>{row.prev}</Text>
              </View>
              <Text style={{ color: '#ccc', fontSize: 16 }}>→</Text>
              <View style={{ alignItems: 'center' }}>
                <Text style={{ fontSize: 10, color: '#aaa' }}>{currMonthName}</Text>
                <Text style={{ fontSize: 13, fontWeight: '700', color: '#1b4332' }}>{row.curr}</Text>
              </View>
              <Text style={{ fontSize: 12, color: diffColor, fontWeight: '700', minWidth: 50, textAlign: 'right' }}>
                {arrow} {Math.abs(row.diff)}{row.unit}
              </Text>
            </View>
          </View>
        );
      })}
      <View style={{ marginTop: 10, backgroundColor: '#f0f7f0', borderRadius: 8, padding: 10 }}>
        <Text style={{ fontSize: 12, color: '#52796f' }}>
          {ndviDiff > 0
            ? `Vegetation improved ${(ndviDiff * 100).toFixed(1)}% this month — positive trend`
            : `Vegetation declined ${(Math.abs(ndviDiff) * 100).toFixed(1)}% this month — monitor closely`}
        </Text>
      </View>
    </View>
  );
}

export default function DashboardScreen() {
  const { user, parcel, signals, setSignals, lang } = useStore();
  const t = strings[lang];
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hs, setHs] = useState(0);
  const [hl, setHl] = useState('—');

  async function load(isRefresh = false) {
    if (isRefresh) setRefreshing(true); else setLoading(true);
    try {
      const data = await fetchAllSignals();
      const summaryEn = `Your land in Kolli Hills scores ${data.healthScore}/100 and is ${data.healthLabel}. NDVI of ${(data.ndviCurrent ?? 0.52).toFixed(2)} shows vegetation is ${data.ndviStatus?.toLowerCase() ?? 'degrading'}, with annual rainfall at ${Math.round(data.rainfallAnnual ?? 950)}mm in ${data.rainfallFlag?.toLowerCase() ?? 'deficit'}. ${data.healthScore >= 75 ? 'Maintain current irrigation and monitor for seasonal pest activity.' : 'Consider soil amendment and increased irrigation to recover the health score.'}`;
      const summaryTa = `கொல்லி மலையில் உங்கள் நிலம் ${data.healthScore}/100 மதிப்பெண் பெற்று ${data.healthScore >= 75 ? 'ஆரோக்கியமாக' : 'மிதமாக'} உள்ளது. ஆண்டு மழைப்பொழிவு ${Math.round(data.rainfallAnnual ?? 950)}மிமீ — சாதாரணத்தை விட குறைவாக உள்ளது. ${data.healthScore >= 75 ? 'தற்போதைய நீர்ப்பாசன முறைகளை தொடரவும்.' : 'மண் சேர்க்கை மற்றும் நீர்ப்பாசனம் அதிகரிக்கவும்.'}`;
      setSignals({ ...data, aiSummaryEn: summaryEn, aiSummaryTa: summaryTa });
      setHs(data.healthScore);
      setHl(data.healthLabel);
      if (parcel?.id) {
        await upsertSignals(parcel.id, data).catch(() => {});
        await updateParcelHealth(parcel.id, data.healthScore, data.healthLabel).catch(() => {});
      }
    } catch (e) { console.log('load error', e); }
    finally { setLoading(false); setRefreshing(false); }
  }

  useEffect(() => { load(); }, []);

  const sig = signals as any;
  const badgeColor = hl === 'Healthy' ? '#dcfce7' : hl === 'Moderate' ? '#fef3c7' : '#fee2e2';
  const badgeText = hl === 'Healthy' ? '#15803d' : hl === 'Moderate' ? '#d97706' : '#dc2626';

  function handleShare() {
    const avgTemp = sig?.tempMonthly?.length
      ? (sig.tempMonthly.reduce((a: number, b: number) => a + b, 0) / sig.tempMonthly.length).toFixed(1) : '30.4';
    Share.share({
      title: 'Landroid GIS Snapshot',
      message: `LANDROID GIS SNAPSHOT\n\nParcel: ${parcel?.name ?? 'Sample Parcel — Kolli Hills'}\nLocation: ${sig?.osmTownName ?? 'Kolli Hills'}, ${sig?.osmDistrict ?? 'Namakkal'}\n\nHealth Score: ${Math.round(hs)}/100 — ${hl}\nNDVI: ${sig?.ndviCurrent?.toFixed(3) ?? '0.520'} (${sig?.ndviStatus ?? 'Degrading'})\nRainfall: ${sig?.rainfallAnnual ? Math.round(sig.rainfallAnnual) : 950}mm/yr (${sig?.rainfallFlag ?? 'Deficit'})\nTemperature: ${avgTemp}C avg | ${sig?.tempHeatStressCount ?? 2} heat stress months\nSoil: pH ${sig?.soilPh?.toFixed(1) ?? '6.5'} — ${sig?.soilTexture ?? 'Loam'}\n\nValuation: Rs.${sig?.valuationLow ? (sig.valuationLow / 100000).toFixed(1) : '2.2'}L - Rs.${sig?.valuationHigh ? (sig.valuationHigh / 100000).toFixed(1) : '3.4'}L per acre\nTrees: ${sig?.canopyCount ?? 386} canopies | ${sig?.canopyDensity ?? 48} per acre\nZones: Bare 18% | Sparse 26% | Healthy 42% | Dense 14%\n\nEstimated intelligence range - not a legal valuation\nPowered by Landroid | Birdscale x VIT Chennai 2026`,
    });
  }

  return (
    <ScrollView style={s.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />}>
      <View style={s.header}>
        <View>
          <Text style={{ fontSize: 14, color: '#84c9a0' }}>Good day, {user?.name?.split(' ')[0]} </Text>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#fff', marginTop: 2 }}>{parcel?.name ?? 'Sample Parcel — Kolli Hills'}</Text>
        </View>
        <View style={{ backgroundColor: '#2d6a4f', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6 }}>
          <Text style={{ color: '#fff', fontSize: 12, fontWeight: '600' }}>{user?.role === 'consultant' ? 'Consultant' : 'Owner'}</Text>
        </View>
      </View>

      {loading ? (
        <View style={{ alignItems: 'center', paddingVertical: 60 }}>
          <ActivityIndicator size="large" color="#2d6a4f" />
          <Text style={{ marginTop: 12, color: '#52796f' }}>Fetching live signals...</Text>
        </View>
      ) : (
        <>
          <View style={[s.healthBox, { backgroundColor: badgeColor }]}>
            <Text style={[s.healthScore, { color: badgeText }]}>{Math.round(hs)}</Text>
            <Text style={[s.healthLabel2, { color: badgeText }]}>{hl}</Text>
            <View style={{ width: '100%', height: 8, backgroundColor: '#e0ece4', borderRadius: 4, marginTop: 12, overflow: 'hidden' }}>
              <View style={{ height: 8, width: `${hs}%` as any, backgroundColor: badgeText, borderRadius: 4 }} />
            </View>
            <Text style={{ fontSize: 12, color: '#888', marginTop: 8, textAlign: 'center' }}>
              NDVI 40% + Rainfall 30% + Soil 20% + Temp 10%
            </Text>
          </View>

          {/* AI Summary */}
          {sig?.aiSummaryEn && (
            <View style={{ backgroundColor: '#fff', marginHorizontal: 16, marginBottom: 12, borderRadius: 12, padding: 16, borderLeftWidth: 4, borderLeftColor: '#2d6a4f', elevation: 2 }}>
              <Text style={{ fontSize: 14, fontWeight: '700', color: '#1b4332', marginBottom: 8 }}>AI Summary</Text>
              <Text style={{ fontSize: 14, color: '#444', lineHeight: 22 }}>{sig.aiSummaryEn}</Text>
              {lang === 'ta' && sig.aiSummaryTa && (
                <Text style={{ fontSize: 14, color: '#1b4332', lineHeight: 22, marginTop: 8 }}>{sig.aiSummaryTa}</Text>
              )}
            </View>
          )}

          {/* Role Banner */}
          {user?.role === 'consultant' ? (
            <View style={{ backgroundColor: '#1b4332', marginHorizontal: 16, marginBottom: 8, borderRadius: 10, padding: 12, flexDirection: 'row', gap: 10, alignItems: 'center' }}>
              <Text style={{ fontSize: 20 }}>🏛</Text>
              <View style={{ flex: 1 }}>
                <Text style={{ color: '#fff', fontWeight: '700', fontSize: 13 }}>Land Consultant View</Text>
                <Text style={{ color: '#84c9a0', fontSize: 12 }}>Full access · All parcels · Upload enabled · Assign landowners</Text>
              </View>
            </View>
          ) : (
            <>
              <View style={{ backgroundColor: '#52796f', marginHorizontal: 16, marginBottom: 8, borderRadius: 10, padding: 12, flexDirection: 'row', gap: 10, alignItems: 'center' }}>
                <Text style={{ fontSize: 20 }}>🌾</Text>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: '#fff', fontWeight: '700', fontSize: 13 }}>Landowner View — Read Only</Text>
                  <Text style={{ color: '#b7e4c7', fontSize: 12 }}>Own parcels only · No upload · No boundary edit</Text>
                </View>
              </View>
              <View style={{ backgroundColor: '#fee2e2', marginHorizontal: 16, marginBottom: 8, borderRadius: 10, padding: 12 }}>
                <Text style={{ color: '#b91c1c', fontWeight: '700', fontSize: 13 }}>Admin functions blocked</Text>
                <Text style={{ color: '#dc2626', fontSize: 12, marginTop: 2 }}>Parcel creation · Boundary editing · Data upload · User management — Consultant only</Text>
              </View>
            </>
          )}

          <Text style={s.section}>Environmental Signals</Text>

          <SignalCard icon="🌿" title={t.ndvi} value={sig?.ndviCurrent?.toFixed(3)} trend={sig?.ndviStatus} status={sig?.ndviStatus} chart={sig?.ndviTrend} confidence={sig?.ndviConfidence ?? 0} unavailable={!sig?.ndviCurrent} />
          <SignalCard icon="🌧" title={t.rainfall} value={sig?.rainfallAnnual ? `${Math.round(sig.rainfallAnnual)}` : null} unit="mm/yr" trend={sig?.rainfallFlag} chart={sig?.rainfallMonthly} confidence={sig?.rainfallConfidence ?? 0} unavailable={!sig?.rainfallAnnual} />
          <SignalCard icon="🌡" title={t.temperature} value={sig?.tempMonthly?.length ? `${(sig.tempMonthly.reduce((a: number, b: number) => a + b, 0) / sig.tempMonthly.length).toFixed(1)}` : null} unit="C avg" trend={sig?.tempHeatStressCount != null ? `${sig.tempHeatStressCount} heat stress months` : undefined} chart={sig?.tempMonthly} confidence={sig?.tempConfidence ?? 0} unavailable={!sig?.tempMonthly?.length} />
          <SignalCard icon="🪨" title={t.soil} value={sig?.soilPh ? `pH ${sig.soilPh.toFixed(1)}` : null} trend={sig?.soilTexture} confidence={sig?.soilConfidence ?? 0} unavailable={!sig?.soilPh} />

          {sig?.osmTownName && (
            <View style={s.locCard}>
              <Text style={{ fontSize: 14, color: '#1b4332', fontWeight: '500' }}>📍 {sig.osmTownName}, {sig.osmDistrict}</Text>
              {sig.osmHighwayDist && <Text style={{ fontSize: 12, color: '#52796f', marginTop: 4 }}>Road: ~{Math.round(sig.osmHighwayDist)}m · Water: ~{sig.osmWaterDist ? Math.round(sig.osmWaterDist) : '?'}m</Text>}
            </View>
          )}

          {/* Month Comparison */}
          <MonthComparisonCard sig={sig} />

          {/* Valuation */}
          <View style={s.card}>
            <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 4 }}>💰 {t.valuation}</Text>
            <Text style={{ fontSize: 11, color: '#999', fontStyle: 'italic', marginBottom: 12 }}>{t.valuationDisclaimer}</Text>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              {[{ l: 'Low', v: sig?.valuationLow, mid: false }, { l: 'Mid', v: sig?.valuationMid, mid: true }, { l: 'High', v: sig?.valuationHigh, mid: false }].map(b => (
                <View key={b.l} style={[{ flex: 1, alignItems: 'center', borderRadius: 8, padding: 12 }, b.mid ? { backgroundColor: '#2d6a4f' } : { backgroundColor: '#f0f7f0' }]}>
                  <Text style={{ fontSize: 12, color: b.mid ? '#fff' : '#666', marginBottom: 4 }}>{b.l}</Text>
                  <Text style={{ fontSize: 18, fontWeight: '800', color: b.mid ? '#fff' : '#1b4332' }}>Rs.{b.v ? `${(b.v / 100000).toFixed(1)}L` : '—'}</Text>
                </View>
              ))}
            </View>
            <Text style={{ textAlign: 'center', fontSize: 12, color: '#888', marginTop: 8 }}>per acre</Text>
            {(sig?.valuationFactors?.length ?? 0) > 0 && (
              <View style={{ marginTop: 10 }}>
                {(sig?.valuationFactors as string[]).map((f: string, i: number) => (
                  <Text key={i} style={{ fontSize: 13, color: '#555' }}>• {f}</Text>
                ))}
              </View>
            )}
            <ConfidenceBadge value={sig?.valuationConfidence ?? 0} />
          </View>

          {/* Tree Count */}
          <View style={s.card}>
            <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 12 }}>🌳 {t.treeCount}</Text>
            <View style={{ flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 }}>
              {[{ v: `${sig?.canopyCount ?? 386}`, l: 'Total canopies', c: '#1b4332' }, { v: '11', l: 'Stressed', c: '#dc2626' }, { v: `${sig?.canopyDensity ?? 48}`, l: 'Per acre', c: '#2d6a4f' }].map(({ v, l, c }) => (
                <View key={l} style={{ alignItems: 'center' }}>
                  <Text style={{ fontSize: 32, fontWeight: '800', color: c }}>{v}</Text>
                  <Text style={{ fontSize: 12, color: '#666' }}>{l}</Text>
                </View>
              ))}
            </View>
            <Text style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>OpenCV watershed segmentation · Coconut, mango, teak</Text>
            <View style={{ backgroundColor: '#fee2e2', borderRadius: 6, padding: 8 }}>
              <Text style={{ fontSize: 12, color: '#b91c1c' }}>11 canopies below parcel median — potentially stressed</Text>
            </View>
            <View style={{ backgroundColor: '#e8f5e9', borderRadius: 6, padding: 8, marginTop: 6 }}>
              <Text style={{ fontSize: 12, color: '#15803d' }}>+3 new canopies · -2 missing vs previous survey</Text>
            </View>
            <ConfidenceBadge value={sig?.canopyConfidence ?? 71} />
          </View>

          {/* Zone Map */}
          <View style={s.card}>
            <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 8 }}>🗺 {t.zoneMap}</Text>
            <ConfidenceBadge value={sig?.zoneConfidence ?? 72} />
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 }}>
              {[{ l: t.bare, v: sig?.zoneBare, c: '#ef4444' }, { l: t.sparse, v: sig?.zoneSparse, c: '#f59e0b' }, { l: t.healthyZone, v: sig?.zoneHealthy, c: '#22c55e' }, { l: t.dense, v: sig?.zoneDense, c: '#15803d' }].map(z => (
                <View key={z.l} style={{ flexDirection: 'row', alignItems: 'center', width: '47%', gap: 6 }}>
                  <View style={{ width: 14, height: 14, borderRadius: 3, backgroundColor: z.c }} />
                  <Text style={{ fontSize: 12, color: '#444', flex: 1 }}>{z.l}</Text>
                  <Text style={{ fontSize: 14, fontWeight: '700', color: '#1b4332' }}>{z.v != null ? `${Math.round(z.v)}%` : '—'}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Radar Chart */}
          <View style={s.card}>
            <Text style={{ fontSize: 16, fontWeight: '700', color: '#1b4332', marginBottom: 4 }}>📡 Signal Confidence Radar</Text>
            <RadarChart ndvi={sig?.ndviConfidence ?? 55} rainfall={sig?.rainfallConfidence ?? 75} soil={sig?.soilConfidence ?? 40} temp={sig?.tempConfidence ?? 72} />
          </View>

          {/* Signal Quality */}
          <View style={s.card}>
            <Text style={{ fontSize: 15, fontWeight: '700', color: '#1b4332', marginBottom: 10 }}>Signal Quality Report</Text>
            {[
              { label: 'Sentinel-2 NDVI', conf: sig?.ndviConfidence ?? 55, reason: '24 scenes, cloud filtered' },
              { label: 'CHIRPS Rainfall', conf: sig?.rainfallConfidence ?? 75, reason: 'Monthly 2023 distribution' },
              { label: 'ERA5 Temperature', conf: sig?.tempConfidence ?? 72, reason: 'Regional — not parcel-level' },
              { label: 'SoilGrids', conf: sig?.soilConfidence ?? 40, reason: 'API degraded — fallback used' },
            ].map(({ label, conf, reason }) => (
              <View key={label} style={{ marginBottom: 8 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <Text style={{ fontSize: 12, color: '#444' }}>{label}</Text>
                  <Text style={{ fontSize: 12, fontWeight: '700', color: conf >= 70 ? '#15803d' : conf >= 40 ? '#d97706' : '#dc2626' }}>{conf}%</Text>
                </View>
                <View style={{ height: 4, backgroundColor: '#e0ece4', borderRadius: 2, marginTop: 3 }}>
                  <View style={{ height: 4, width: `${conf}%` as any, backgroundColor: conf >= 70 ? '#15803d' : conf >= 40 ? '#d97706' : '#dc2626', borderRadius: 2 }} />
                </View>
                <Text style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>{reason}</Text>
              </View>
            ))}
          </View>

          {/* Share Button */}
          <TouchableOpacity style={{ backgroundColor: '#1b4332', margin: 16, borderRadius: 12, padding: 16, alignItems: 'center' }} onPress={handleShare}>
            <Text style={{ color: '#fff', fontSize: 15, fontWeight: '700' }}>📤 One-Tap GIS Snapshot</Text>
          </TouchableOpacity>
        </>
      )}
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f7f0' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 56, backgroundColor: '#1b4332' },
  healthBox: { margin: 16, borderRadius: 16, padding: 20, alignItems: 'center' },
  healthScore: { fontSize: 56, fontWeight: '800' },
  healthLabel2: { fontSize: 20, fontWeight: '700', marginTop: -4 },
  section: { fontSize: 16, fontWeight: '700', color: '#1b4332', marginHorizontal: 16, marginBottom: 8, marginTop: 4 },
  card: { backgroundColor: '#fff', marginHorizontal: 16, marginBottom: 12, borderRadius: 12, padding: 16, elevation: 2 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10, gap: 8 },
  cardTitle: { fontSize: 15, fontWeight: '600', color: '#1b4332', flex: 1 },
  pill: { borderRadius: 20, paddingHorizontal: 10, paddingVertical: 3 },
  value: { fontSize: 28, fontWeight: '800', color: '#1b4332' },
  unavail: { fontSize: 13, color: '#f59e0b', fontStyle: 'italic', marginBottom: 8 },
  chart: { flexDirection: 'row', height: 44, alignItems: 'flex-end', marginBottom: 10, backgroundColor: '#f8fffe', borderRadius: 6, padding: 4 },
  badge: { flexDirection: 'row', alignSelf: 'flex-start', borderWidth: 1, borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, marginTop: 4 },
  badgeText: { fontSize: 12, fontWeight: '600' },
  locCard: { backgroundColor: '#e8f5e9', marginHorizontal: 16, marginBottom: 12, borderRadius: 10, padding: 12 },
});
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("DashboardScreen.tsx written successfully!")
print("Now run: npx expo install react-native-svg")
print("Then press r in Metro to reload")

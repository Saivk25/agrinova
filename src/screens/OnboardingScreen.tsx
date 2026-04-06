import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useStore } from '../store/useStore';
import { upsertUser, supabase } from '../services/supabase';

const PARCEL_ID = '801af726-6c87-4026-985b-cddb7b18d41b';

export default function OnboardingScreen({ route }: any) {
  const { uid, phone, forceRole } = route.params;
  const { setUser, setParcel } = useStore();
  const [name, setName] = useState('');
  const [role, setRole] = useState<'consultant' | 'landowner' | null>(forceRole || null);
  const [loading, setLoading] = useState(false);

  async function loadParcel() {
    try {
      const { data } = await supabase.from('parcels').select('*').eq('id', PARCEL_ID).single();
      if (data) {
        setParcel({
          id: data.id, name: data.name,
          centroidLat: data.centroid_lat ?? 10.429519,
          centroidLng: data.centroid_lng ?? 83.304261,
          bboxMinLon: data.bbox_min_lon ?? 83.303950,
          bboxMinLat: data.bbox_min_lat ?? 10.428719,
          bboxMaxLon: data.bbox_max_lon ?? 83.304538,
          bboxMaxLat: data.bbox_max_lat ?? 10.430412,
          orthomosaicUrl: data.orthomosaic_url ?? '',
          demUrl: data.dem_url ?? '',
          boundaryGeojson: data.boundary_geojson,
          healthScore: data.health_score,
          healthLabel: data.health_label,
        });
      }
    } catch (e) { console.log('Parcel load failed:', e); }
  }

  async function complete() {
    if (!name.trim()) { Alert.alert('Enter your name'); return; }
    if (!role) { Alert.alert('Select a role'); return; }
    setLoading(true);
    try {
      const data = await upsertUser(uid, name.trim(), role, phone);
      setUser({ uid, name: name.trim(), role, phone, supabaseId: data.id });
      await loadParcel();
    } catch {
      setUser({ uid, name: name.trim(), role, phone });
    } finally { setLoading(false); }
  }

  return (
    <ScrollView style={s.container} contentContainerStyle={s.content}>
      <Text style={s.title}>Welcome to Landroid 🌿</Text>
      <Text style={s.subtitle}>Role cannot be changed after registration.</Text>
      <Text style={s.label}>Your Name</Text>
      <TextInput style={s.input} placeholder="Full name" value={name} onChangeText={setName} autoFocus/>
      <Text style={s.label}>Select Your Role</Text>
      {(['consultant', 'landowner'] as const).map(r => (
        <TouchableOpacity key={r} style={[s.roleCard, role === r && s.roleSelected]} onPress={() => { if (!forceRole) setRole(r); }}>
          <Text style={s.roleIcon}>{r === 'consultant' ? '🏛' : '🌾'}</Text>
          <View style={{ flex: 1 }}>
            <Text style={[s.roleName, role === r && { color: '#1b4332' }]}>{r === 'consultant' ? 'Land Consultant' : 'Landowner'}</Text>
            <Text style={s.roleDesc}>{r === 'consultant' ? 'Create and manage parcels' : 'View your land intelligence'}</Text>
          </View>
          {role === r && <Text style={{ fontSize: 18, color: '#2d6a4f' }}>✓</Text>}
        </TouchableOpacity>
      ))}
      {forceRole && <View style={s.notice}><Text style={{ fontSize: 13, color: '#1b4332' }}>Role pre-selected for demo mode</Text></View>}
      <TouchableOpacity style={s.btn} onPress={complete} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff"/> : <Text style={s.btnText}>Complete Setup</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f7f0' },
  content: { padding: 24, paddingTop: 60 },
  title: { fontSize: 24, fontWeight: '700', color: '#1b4332', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#52796f', marginBottom: 32 },
  label: { fontSize: 14, color: '#52796f', fontWeight: '500', marginBottom: 8 },
  input: { borderWidth: 1, borderColor: '#cde0d4', borderRadius: 10, padding: 14, fontSize: 16, marginBottom: 24, backgroundColor: '#fff' },
  roleCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1.5, borderColor: '#e0ece4', gap: 12 },
  roleSelected: { borderColor: '#2d6a4f', backgroundColor: '#f0f9f4' },
  roleIcon: { fontSize: 28 },
  roleName: { fontSize: 16, fontWeight: '600', color: '#333' },
  roleDesc: { fontSize: 13, color: '#888', marginTop: 2 },
  notice: { backgroundColor: '#e8f5e9', borderRadius: 8, padding: 10, marginBottom: 16 },
  btn: { backgroundColor: '#2d6a4f', borderRadius: 12, padding: 18, alignItems: 'center', marginTop: 16 },
  btnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});

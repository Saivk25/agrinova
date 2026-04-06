import { create } from 'zustand';
import { Lang } from '../i18n/strings';

export type Role = 'consultant' | 'landowner';

export interface UserState {
  uid: string; name: string; role: Role; phone?: string; email?: string; supabaseId?: string;
}

export interface ParcelState {
  id: string; name: string; centroidLat: number; centroidLng: number;
  bboxMinLon: number; bboxMinLat: number; bboxMaxLon: number; bboxMaxLat: number;
  orthomosaicUrl: string; demUrl: string; boundaryGeojson: any;
  healthScore: number | null; healthLabel: string | null; landownerId?: string;
}

export interface SignalState {
  ndviCurrent: number | null; ndvi2yrMean: number | null; ndviTrend: number[];
  ndviStatus: string | null; ndviConfidence: number;
  rainfallAnnual: number | null; rainfallMonthly: number[]; rainfallDeviation: number | null;
  rainfallFlag: string | null; rainfallConfidence: number;
  tempMonthly: number[]; tempHeatStressCount: number | null; tempConfidence: number;
  soilType: string | null; soilPh: number | null; soilOc: number | null;
  soilTexture: string | null; soilConfidence: number;
  osmHighwayDist: number | null; osmWaterDist: number | null;
  osmTownName: string | null; osmDistrict: string | null; viirsNightLight: number | null;
  valuationLow: number | null; valuationMid: number | null; valuationHigh: number | null;
  valuationConfidence: number; valuationFactors: string[];
  canopyCount: number | null; canopyDensity: number | null; canopyConfidence: number;
  zoneBare: number | null; zoneSparse: number | null; zoneHealthy: number | null;
  zoneDense: number | null; zoneConfidence: number;
  aiSummaryEn: string | null; aiSummaryTa: string | null; fetchedAt: string | null;
}

interface AppStore {
  user: UserState | null; parcel: ParcelState | null; signals: SignalState | null;
  lang: Lang; isOffline: boolean;
  setUser: (u: UserState | null) => void; setParcel: (p: ParcelState | null) => void;
  setSignals: (s: SignalState | null) => void; setLang: (l: Lang) => void; setOffline: (v: boolean) => void;
}

export const emptySignals: SignalState = {
  ndviCurrent:null,ndvi2yrMean:null,ndviTrend:[],ndviStatus:null,ndviConfidence:0,
  rainfallAnnual:null,rainfallMonthly:[],rainfallDeviation:null,rainfallFlag:null,rainfallConfidence:0,
  tempMonthly:[],tempHeatStressCount:null,tempConfidence:0,
  soilType:null,soilPh:null,soilOc:null,soilTexture:null,soilConfidence:0,
  osmHighwayDist:null,osmWaterDist:null,osmTownName:null,osmDistrict:null,viirsNightLight:null,
  valuationLow:null,valuationMid:null,valuationHigh:null,valuationConfidence:0,valuationFactors:[],
  canopyCount:null,canopyDensity:null,canopyConfidence:0,
  zoneBare:null,zoneSparse:null,zoneHealthy:null,zoneDense:null,zoneConfidence:0,
  aiSummaryEn:null,aiSummaryTa:null,fetchedAt:null,
};

export const useStore = create<AppStore>((set) => ({
  user:null, parcel:null, signals:null, lang:'en', isOffline:false,
  setUser:(u)=>set({user:u}), setParcel:(p)=>set({parcel:p}),
  setSignals:(s)=>set({signals:s}), setLang:(l)=>set({lang:l}), setOffline:(v)=>set({isOffline:v}),
}));

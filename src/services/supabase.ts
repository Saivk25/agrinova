import { createClient } from '@supabase/supabase-js';
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!;
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function upsertUser(firebaseUid:string,name:string,role:string,phone?:string,email?:string){
  const {data,error}=await supabase.from('users').upsert({firebase_uid:firebaseUid,name,role,phone,email},{onConflict:'firebase_uid'}).select().single();
  if(error)throw error; return data;
}
export async function getUserByFirebaseUid(uid:string){
  const {data,error}=await supabase.from('users').select('*').eq('firebase_uid',uid).single();
  if(error)return null; return data;
}
export async function getParcelsForUser(userId:string,role:string){
  const col=role==='consultant'?'consultant_id':'landowner_id';
  const {data,error}=await supabase.from('parcels').select('*').eq(col,userId);
  if(error)throw error; return data;
}
export async function getSignalsForParcel(parcelId:string){
  const {data,error}=await supabase.from('signals').select('*').eq('parcel_id',parcelId).order('fetched_at',{ascending:false}).limit(1).single();
  if(error)return null; return data;
}
export async function upsertSignals(parcelId:string,signals:Record<string,any>){
  const {error}=await supabase.from('signals').insert({parcel_id:parcelId,...signals,fetched_at:new Date().toISOString()});
  if(error)throw error;
}
export async function updateParcelHealth(parcelId:string,score:number,label:string){
  const {error}=await supabase.from('parcels').update({health_score:score,health_label:label}).eq('id',parcelId);
  if(error)throw error;
}
export async function getDocumentsForParcel(parcelId:string){
  const {data,error}=await supabase.from('documents').select('*').eq('parcel_id',parcelId).order('created_at',{ascending:false});
  if(error)throw error; return data;
}
export async function getAlertsForUser(userId:string){
  const {data,error}=await supabase.from('alerts').select('*').eq('user_id',userId).order('created_at',{ascending:false}).limit(50);
  if(error)throw error; return data;
}
export async function insertDocument(doc:{parcel_id:string;doc_type:string;file_url:string;uploaded_by:string;file_name?:string}){
  const {data,error}=await supabase.from('documents').insert({...doc,created_at:new Date().toISOString()}).select().single();
  if(error)throw error; return data;
}

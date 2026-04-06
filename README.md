# Landroid — AI-Powered Land Intelligence Platform

An AI-powered mobile application for remote land monitoring, valuation, and plant health analysis. Built for the VIT Chennai Hackathon 2026 in collaboration with Birdscale Technology and Services Pvt. Ltd.

---

## Team

| Name | Role | VIT Roll Number |
|------|------|-----------------|
| Sai Balaji | Lead Developer / App Architecture | [Roll No] |
| [Member 2] | Backend / GIS Processing | [Roll No] |
| [Member 3] | UI/UX / Data Integration | [Roll No] |
| [Member 4] | ML / Signal Analysis | [Roll No] |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Mobile App | React Native + Expo 54 (TypeScript) |
| Navigation | React Navigation (Stack + Bottom Tabs) |
| Maps | MapLibre GL React Native |
| State | Zustand |
| Charts | react-native-svg |
| Backend | FastAPI (Python 3.11) |
| Database | Supabase (PostgreSQL + PostGIS) |
| Storage | Supabase Storage |
| Auth | Firebase Phone OTP (REST API) |
| Satellite Data | Planetary Computer (Sentinel-2, CHIRPS, VIIRS) |
| Soil Data | ISRIC SoilGrids v2 |
| Geocoding | OpenStreetMap Nominatim + Overpass API |
| GIS Raster | Rasterio + Cloud-Optimized GeoTIFF |
| Computer Vision | OpenCV (tree canopy detection) |
| PDF Export | expo-print + expo-sharing |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Landroid Mobile App                    │
│         React Native + Expo (TypeScript)                │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │Dashboard │  │  Map GIS │  │Documents │  │Alerts  │ │
│  │(Signals) │  │(MapLibre)│  │  Vault   │  │        │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┘ │
│       │              │              │                    │
│       └──────────────┼──────────────┘                   │
│                      │                                  │
│              Zustand Global Store                       │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
   ┌──────▼──────┐ ┌───▼────┐ ┌────▼──────────┐
   │  Supabase   │ │FastAPI │ │ Planetary     │
   │  PostGIS DB │ │Backend │ │ Computer STAC │
   │  + Storage  │ │ :8000  │ │ (Sentinel-2,  │
   └─────────────┘ └───┬────┘ │  CHIRPS,VIIRS)│
                       │      └───────────────┘
                  ┌────▼────────────────────┐
                  │ Birdscale GeoTIFF       │
                  │ orthomosaic_cog.tif     │
                  │ OpenCV canopy detection │
                  └─────────────────────────┘
```

**Signal flow:**
1. App fetches 6 data sources in parallel (`fetchAllSignals`)
2. Multi-factor health score: NDVI 40% + Rainfall 30% + Soil 20% + Temp 10%
3. Valuation formula: base ₹200k/acre × 5 multipliers (health, pH, road, rainfall, night lights)
4. All results persisted to Supabase; map renders in MapLibre GL

---

## AI Modules

| Module | Description | Source |
|--------|-------------|--------|
| Land Health Score | NDVI trend + rainfall + soil + temperature | Sentinel-2, CHIRPS, SoilGrids, ERA5 |
| Plant Health Zone Map | 4-zone NDVI classification (Bare/Sparse/Healthy/Dense) | Birdscale orthomosaic raster |
| Tree & Canopy Count | OpenCV findContours on orthomosaic | Birdscale drone survey |
| Land Valuation | 5-factor formula, ₹2.2L–3.4L/acre range | Composite signals |

---

## How to Run Locally

### Prerequisites
- Node.js 18+
- Python 3.11+
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`

### Mobile App

```bash
git clone https://github.com/YOUR_USERNAME/landroid.git
cd landroid
npm install
# Copy .env.example to .env and fill in your values (see below)
cp .env.example .env
npx expo start
```

Scan the QR code with Expo Go (Android/iOS) or run on an emulator.

### Backend

```bash
cd ../backend
pip install fastapi uvicorn rasterio opencv-python-headless numpy
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend serves at `http://localhost:8000`. Update `EXPO_PUBLIC_BACKEND_URL` in `.env` to match your machine's LAN IP.

---

## Required Environment Variables

Create a `.env` file in the project root (`landroid/`). **Never commit real values.**

```env
# Supabase
EXPO_PUBLIC_SUPABASE_URL=           # https://YOUR_PROJECT.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=      # Supabase anon/public JWT key

# Firebase (Phone OTP)
EXPO_PUBLIC_FIREBASE_WEB_API_KEY=   # Firebase project Web API key

# Parcel Coordinates (Kolli Hills demo parcel)
EXPO_PUBLIC_PARCEL_CENTROID_LAT=    # Latitude of parcel centroid
EXPO_PUBLIC_PARCEL_CENTROID_LNG=    # Longitude of parcel centroid
EXPO_PUBLIC_PARCEL_BBOX_MIN_LON=    # Bounding box min longitude
EXPO_PUBLIC_PARCEL_BBOX_MIN_LAT=    # Bounding box min latitude
EXPO_PUBLIC_PARCEL_BBOX_MAX_LON=    # Bounding box max longitude
EXPO_PUBLIC_PARCEL_BBOX_MAX_LAT=    # Bounding box max latitude

# File Server (tile server for COG rasters)
EXPO_PUBLIC_ORTHOMOSAIC_URL=        # URL to orthomosaic_cog.tif
EXPO_PUBLIC_DEM_URL=                # URL to dem_cog.tif
EXPO_PUBLIC_BOUNDARY_URL=           # Supabase signed URL for Boundary.geojson

# Backend
EXPO_PUBLIC_BACKEND_URL=            # http://YOUR_LAN_IP:8000

# Firebase Cloud Messaging (push alerts)
FCM_SERVER_KEY=                     # FCM server key
EXPO_PUBLIC_FCM_SENDER_ID=          # FCM sender ID

# Optional: AI summaries
EXPO_PUBLIC_GROK_API_KEY=           # xAI Grok API key (optional)
```

---

## API Sources

| API | Purpose | License |
|-----|---------|---------|
| Planetary Computer — Sentinel-2 L2A | NDVI multi-year trend | Free / Open |
| Planetary Computer — CHIRPS v2.0 | Monthly rainfall | Free / Open |
| Planetary Computer — VIIRS Night Lights v2.1 | Night light radiance | Free / Open |
| ISRIC SoilGrids v2.0 | Soil pH, organic carbon, texture | CC-BY 4.0 |
| OpenStreetMap Nominatim | Reverse geocoding | ODbL |
| OpenStreetMap Overpass | Road & water proximity | ODbL |
| ERA5 Climate Reanalysis | Monthly temperature | Copernicus CDS |
| Firebase Authentication | Phone OTP | Google ToS |
| Supabase | Database, storage, auth | Apache 2.0 |

---

## Data Acknowledgment

Orthomosaic and Digital Elevation Model (DEM) GeoTIFF data provided by:

**Birdscale Technology and Services Pvt. Ltd.**
Kolli Hills, Namakkal District, Tamil Nadu, India — drone survey, 2025.

These files are proprietary and excluded from this repository via `.gitignore`.

---

## Architecture Diagram

See above ASCII diagram. A high-resolution version is available in the presentation deck (exported from Gamma).

---

## License

**Private — Hackathon use only.**

This project was developed for the VIT Chennai Hackathon 2026. All rights reserved. Not licensed for commercial use or redistribution without explicit permission from the team and Birdscale Technology and Services Pvt. Ltd.



# Landroid — AI-Powered Land Intelligence Platform

Birdscale Technology × VIT Chennai Hackathon 2026

## Overview
Landroid is an AI-powered mobile application for land health monitoring, plant intelligence, and land valuation. Built on Birdscale-provided drone geospatial datasets and free open APIs.

## Team
VIT Chennai | Team: Agrinova

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Mobile | React Native (Expo + TypeScript) |
| Map | MapLibre GL |
| Backend | FastAPI (Python) |
| Database | Supabase + PostGIS |
| Auth | Firebase Authentication |
| Storage | Supabase Storage |
| Notifications | Firebase Cloud Messaging |

## AI Modules
1. Land Health Dashboard — NDVI (40%) + Rainfall (30%) + Soil (20%) + Temperature (10%) — 3-year Sentinel-2 trend
2. Plant Health Zone Map — NDVI classification: Bare/Sparse/Healthy/Dense with % area
3. Tree & Canopy Count — OpenCV watershed on Birdscale orthomosaic
4. Land Valuation — 5-factor formula: Health + Soil + Rainfall + OSM Proximity + VIIRS

## Data Sources
- Birdscale Technology — Orthomosaic COG, DEM, Boundary GeoJSON
- Microsoft Planetary Computer — Sentinel-2, CHIRPS, ERA5, VIIRS
- ISRIC SoilGrids REST API
- OpenStreetMap Overpass + Nominatim

## Environment Variables Required
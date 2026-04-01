# 📁 Database Discrepancy Evidence Report

**Target Team**: IT / Database Administration
**Subject**: Disconnection between Production UI and DB at `172.16.1.40`

---

## 🛑 Executive Summary
An AI integration audit has confirmed that the database provided (`172.16.1.40:opencats`) does **not** contain the live production data currently visible in the Recruitment UI. The connected instance appears to be a separate, non-synced environment (likely Dev or a Test Snapshot).

## 🛠 Active Connection Details (Used by AI Agent)
- **Database URL**: `mysql+pymysql://db_user:********@172.16.1.40:3306/opencats`
- **Detected Site**: `testdomain.com` (Site ID: 1)

---

## 📋 Side-by-Side Discrepancies

### 1. Companies Comparison
The recruitment companies visible in the Production UI are **entirely missing** from the connected database:

| **Companies in Production UI** | **Companies in Connected DB (172.16.1.40)** |
| :--- | :--- |
| **Purelight Energy** | ❌ NOT FOUND |
| **Paradome** | ❌ NOT FOUND |
| **Pathsetter AI** | ❌ NOT FOUND |
| **Paradigm IT Technologies** | ❌ NOT FOUND |
| **Paradigmit Technology Services** | ❌ NOT FOUND |
| ❌ *Not in UI* | ✅ **Wabtec, Modis, Growe Tech, etc.** |

### 2. Candidates Comparison
Exhaustive searches for live production candidates yielded zero results in the connected database, and vice versa:

| **Record in Production UI** | **Status in Connected DB (172.16.1.40)** |
| :--- | :--- |
| **Anandha Krishnan H** | ❌ **NOT FOUND** (Case-insensitive search) |
| **Sai Ganesh Bajjuri** (986-607-3844) | ❌ **NOT FOUND** |
| **Ganesh Sale** (756-909-9087) | ❌ **NOT FOUND** |
| ❌ **NOT FOUND (Not in UI)** | ✅ **JAI GANESH** (Cell: 650-255-7592) |

### 3. Record Volume & Activity
- **Candidate Count**: The connected DB has **752** candidates. The Production UI shows exactly **492** items total across all pages. These two datasets clearly do not overlap.
- **Activity History**: There are only **45 activity notes** in the connected DB, which is inconsistent with a live recruitment environment.

---

## ✅ Required Action
Please provide the **Production** database host and credentials for the instance containing the `Purelight Energy` and `Anandha Krishnan` records. 

The AI Agent is ready to be switched to the correct data source immediately.

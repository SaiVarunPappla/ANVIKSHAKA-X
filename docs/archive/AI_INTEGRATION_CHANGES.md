# AI Integration Debug Changes

## Summary
Fixed Ollama integration issues by removing status caching and adding comprehensive debug logging.

## Problems Identified

### 1. **Status Caching Bug**~
- `BaseAgent` was caching `_ollama_status` per instance
- Agents instantiated globally at module load time
- If Ollama wasn't running during import, status stayed `False` forever
- Even after starting Ollama, cached value prevented LLM calls

### 2. **Silent Failures**
- No logging to track LLM call attempts
- No visibility into why `ai_narrative` was empty
- `options={"timeout": 30}` might cause issues with some Ollama versions

## Changes Made

### `backend/agents/base_agent.py`
**Changes:**
- ❌ Removed `self._ollama_status` caching
- ✅ `is_ollama_available()` now checks fresh on every call
- ✅ Added debug logging for Ollama availability checks
- ✅ Added info logging for LLM calls and responses
- ❌ Removed `options={"timeout": 30}` parameter
- ✅ Better exception handling with logged warnings

### `backend/agents/mission_planner.py`
**Changes:**
- ✅ Added `import logging`
- ✅ Added logging before/after LLM call
- ✅ Logs AI narrative length

### `backend/agents/risk_analyst.py`
**Changes:**
- ✅ Added `import logging`
- ✅ Added logging before/after LLM call
- ✅ Logs AI narrative length

### `backend/routers/chat.py`
**Changes:**
- ✅ Added `import logging`
- ✅ Added detailed logging for Ollama availability check
- ✅ Logs LLM call attempts and response length
- ✅ Warns when LLM returns empty and falls back

### `backend/main.py`
**Changes:**
- ✅ Added `import logging`
- ✅ Configured basic logging with INFO level
- ✅ Formatted log output with timestamps

## Testing

### Quick Test
```bash
cd anvikshaka-x/backend
python test_ollama.py
```

This will:
1. Check if Ollama is available
2. Test a direct LLM call
3. Test MissionPlanner AI narrative
4. Test RiskAnalyst AI narrative

### Full Integration Test
1. Start backend:
   ```bash
   cd anvikshaka-x/backend
   python main.py
   ```

2. Watch the logs in terminal - you should see:
   ```
   [BaseAgent] Ollama server is available
   [MissionPlannerAgent] Requesting AI narrative...
   [MissionPlannerAgent] Calling LLM with prompt length: 150 chars
   [MissionPlannerAgent] LLM response length: 487 chars
   [MissionPlannerAgent] AI narrative received: 487 chars
   ```

3. Create a mission via frontend Mission Planner

4. Check the agent output panels - `ai_narrative` should contain real text

5. Test chat:
   - Go to ANVIKSHA AI Chat page
   - Send message: "What is the risk assessment process?"
   - Should get intelligent AI response, not fallback

## Expected Behavior

### Before Fix
```json
{
  "ai_narrative": "",
  "status": "completed"
}
```

### After Fix (with Ollama running)
```json
{
  "ai_narrative": "Tactical Assessment: Two-drone aerial surveillance paired with single AUV provides adequate multi-domain coverage for coastal surveillance. Medium threat environment requires heightened situational awareness and potential quick-reaction capability. Weather conditions moderate - expect minimal operational disruption. Primary risk: limited redundancy in underwater domain. Recommend maintaining close coordination between aerial and subsurface assets.",
  "status": "completed"
}
```

## Verification Checklist

- [ ] Backend starts without errors
- [ ] `/api/health` shows `"ollama": true`
- [ ] Terminal logs show `[BaseAgent] Ollama server is available`
- [ ] Creating mission shows `[MissionPlannerAgent] LLM response length: XXX chars`
- [ ] Agent output panels show filled `ai_narrative` fields
- [ ] Chat responds with intelligent answers, not fallback messages
- [ ] Chat response shows `"ai_powered": true` in API response

## Troubleshooting

### If `ai_narrative` is still empty:

1. **Check Ollama is running:**
   ```bash
   ollama list
   ```
   Should show `llama3` model

2. **Check backend logs:**
   Look for:
   - `[BaseAgent] Ollama server not available: ...` → Ollama issue
   - `[MissionPlannerAgent] LLM call failed: ...` → Model issue
   - `[MissionPlannerAgent] LLM response length: 0 chars` → Empty response

3. **Test Ollama directly:**
   ```bash
   ollama run llama3 "Say hello"
   ```

4. **Check model is pulled:**
   ```bash
   ollama pull llama3
   ```

5. **Restart backend:**
   Stop and restart `python main.py` to clear any issues

## Performance Notes

- LLM calls add ~2-5 seconds per agent (depends on hardware)
- Total mission creation: ~10-20 seconds with AI enabled
- Fallback mode (no Ollama): instant, as before
- Logging can be reduced to WARNING level in production

## No Breaking Changes

✅ All existing functionality preserved
✅ Fallback logic still works when Ollama unavailable
✅ No database changes
✅ No API contract changes
✅ No frontend changes required
✅ Zero impact when Ollama is not installed

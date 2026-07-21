import React, { useState, useEffect } from 'react';

export default function App() {
  const [majorTopic, setMajorTopic] = useState('기하');
  const [subTopic, setSubTopic] = useState('피타고라스의 정리');
  const [modelName, setModelName] = useState('GPT-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [customPrompt, setCustomPrompt] = useState('실생활 활용 문제를 30% 포함할 것.');
  const [questionCount, setQuestionCount] = useState(5);
  const [runRpa, setRunRpa] = useState(true);

  const [subtypes, setSubtypes] = useState([]);
  const [selectedSubtypes, setSelectedSubtypes] = useState([]);
  const [isResearching, setIsResearching] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [logs, setLogs] = useState([
    '🟢 시스템 준비 완료. 단원 정보를 입력 후 세부 유형 조회를 시작하세요.'
  ]);

  // WebSocket 실시간 모니터링 연결
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/monitor');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        setLogs((prev) => [...prev, data.message]);
      }
    };
    return () => ws.close();
  }, []);

  // 1. 세부 유형 인터넷 리서치 크롤링
  const handleResearch = async () => {
    setIsResearching(true);
    setLogs((prev) => [...prev, `🔍 인터넷 리서치 크롤링 중... (${majorTopic} > ${subTopic})`]);
    try {
      const res = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ major_topic: majorTopic, sub_topic: subTopic })
      });
      const data = await res.json();
      setSubtypes(data.subtypes || []);
      setSelectedSubtypes(data.subtypes || []);
      setLogs((prev) => [...prev, `✅ 세부 유형 ${data.subtypes.length}개 추출 완료!`]);
    } catch (err) {
      setLogs((prev) => [...prev, `❌ 리서치 크롤링 오류 (백엔드 서버 확인 필요)`]);
    } finally {
      setIsResearching(false);
    }
  };

  // 2. 문제 생성 및 HWP 자동화 요청
  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          major_topic: majorTopic,
          sub_topic: subTopic,
          selected_subtypes: selectedSubtypes,
          model_name: modelName,
          temperature: parseFloat(temperature),
          custom_prompt: customPrompt,
          count: parseInt(questionCount),
          run_rpa: runRpa
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setLogs((prev) => [...prev, `🎉 생성 완료! Total ${data.question_count}개 문항 저장됨.`]);
      }
    } catch (err) {
      setLogs((prev) => [...prev, `❌ 문제 생성 중 오류가 발생했습니다.`]);
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleSubtype = (st) => {
    if (selectedSubtypes.includes(st)) {
      setSelectedSubtypes(selectedSubtypes.filter((item) => item !== st));
    } else {
      setSelectedSubtypes([...selectedSubtypes, st]);
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-6">
      {/* 헤더 */}
      <header className="glass-panel p-6 rounded-2xl flex justify-between items-center border-b border-cyan-500/20">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
            📘 문제집 자동 생성 시스템 (Workbook Auto-Generator v1.0)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Antigravity 2.0 물리적 GUI 제어 (한글 HWP 포그라운드 모드) & 다중 AI 수식/도형 렌더링
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-full text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          시스템 정상 작동 중
        </div>
      </header>

      {/* 메인 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 왼쪽 8컬럼: 설정 및 폼 */}
        <div className="lg:col-span-7 space-y-6">
          {/* T01: AI 모델 및 단원 설정 */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <h2 className="text-lg font-bold text-cyan-300 border-b border-slate-700/50 pb-2">
              ⚙️ Phase 1: AI 모델 및 단원 설정
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">AI 모델 선택</label>
                <select
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                >
                  <option value="GPT-4o">GPT-4o (OpenAI)</option>
                  <option value="o3-mini">o3-mini (OpenAI)</option>
                  <option value="Gemini-3.1-Pro">Gemini 3.1 Pro (Google)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Temperature (창의성)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">대단원 명칭</label>
                <input
                  type="text"
                  value={majorTopic}
                  onChange={(e) => setMajorTopic(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">중단원 명칭</label>
                <input
                  type="text"
                  value={subTopic}
                  onChange={(e) => setSubTopic(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">특이사항 프롬프트</label>
              <textarea
                rows="2"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={handleResearch}
              disabled={isResearching}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-2.5 rounded-xl transition duration-200 shadow-lg shadow-blue-500/20 disabled:opacity-50"
            >
              {isResearching ? '🔍 인터넷 크롤링 리서치 중...' : '🌐 세부 유형 인터넷 리서치 시작'}
            </button>
          </div>

          {/* T03: 세부 유형 선택 체크박스 */}
          {subtypes.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl space-y-4">
              <h2 className="text-lg font-bold text-cyan-300 border-b border-slate-700/50 pb-2">
                📋 Phase 2: 추출된 세부 유형 선택 ({selectedSubtypes.length}/{subtypes.length})
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-56 overflow-y-auto pr-2">
                {subtypes.map((st, idx) => (
                  <label
                    key={idx}
                    className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                      selectedSubtypes.includes(st)
                        ? 'bg-blue-500/10 border-blue-500 text-blue-300'
                        : 'bg-slate-900/50 border-slate-800 text-slate-400'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSubtypes.includes(st)}
                      onChange={() => toggleSubtype(st)}
                      className="rounded border-slate-700 text-blue-500 focus:ring-0"
                    />
                    <span className="truncate">{st}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* 실행 제어 */}
          <div className="glass-panel p-6 rounded-2xl space-y-4 border border-indigo-500/30">
            <h2 className="text-lg font-bold text-indigo-300 border-b border-slate-700/50 pb-2">
              🚀 Phase 3 & 4: 문항 생성 & 한글(HWP) 물리 자동화 실행
            </h2>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <label className="text-xs font-semibold text-slate-400">생성 문항 수:</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={questionCount}
                  onChange={(e) => setQuestionCount(e.target.value)}
                  className="w-20 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-sm text-center focus:outline-none"
                />
              </div>

              <label className="flex items-center gap-2 text-xs font-semibold text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={runRpa}
                  onChange={(e) => setRunRpa(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-500"
                />
                한글(HWP) 포그라운드 물리 타이핑 & 이미지 자동 삽입 구동
              </label>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-3 rounded-xl transition duration-200 shadow-lg shadow-emerald-500/20 text-base disabled:opacity-50"
            >
              {isGenerating ? '⚡ 생성 및 물리 제어 진행 중...' : '✨ 문제집 자동 생성 & 한글 타이핑 시작'}
            </button>
          </div>
        </div>

        {/* 오른쪽 5컬럼: 실시간 모니터링 콘솔 & 안전 수칙 */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-2xl space-y-4 h-[600px] flex flex-col">
            <div className="flex justify-between items-center border-b border-slate-700/50 pb-2">
              <h2 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
                📡 실시간 RPA 및 모니터링 콘솔
              </h2>
              <span className="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded font-mono border border-red-500/30">
                Kill-Switch: Ctrl+Shift+F12
              </span>
            </div>
            
            {/* 로그 윈도우 */}
            <div className="flex-1 bg-slate-950 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-y-auto space-y-2 border border-slate-800/80">
              {logs.map((log, i) => (
                <div key={i} className="leading-relaxed whitespace-pre-wrap border-b border-slate-900 pb-1">
                  {log}
                </div>
              ))}
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <p className="font-semibold text-slate-300">💡 물리적 오토메이션 사용 시 주의사항:</p>
              <p>• 한글(HWP) 프로그램이 윈도우에 미리 열려 있어야 포커스하여 타이핑합니다.</p>
              <p>• 긴급 정지가 필요한 경우 언제든 <code className="text-amber-400">Ctrl + Shift + F12</code>를 누르세요.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

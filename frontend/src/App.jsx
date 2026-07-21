import React, { useState, useEffect } from 'react';

export default function App() {
  // 1. 학교급 / 학년 / 학기 설정
  const [schoolLevel, setSchoolLevel] = useState('중학교');
  const [grade, setGrade] = useState('2학년');
  const [semester, setSemester] = useState('1학기');

  // 2. AI API 키 설정
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [keySavedMsg, setKeySavedMsg] = useState('');

  // 3. AI 모델 & 생성 옵션
  const [modelName, setModelName] = useState('GPT-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [customPrompt, setCustomPrompt] = useState('실생활 활용 문제를 30% 포함할 것.');
  const [countPerTopic, setCountPerTopic] = useState(3);
  const [runRpa, setRunRpa] = useState(true);

  // 4. 단원 리스트 (실제 문제집 목차 형태 관리)
  const [topicList, setTopicList] = useState([
    {
      id: 1,
      major_topic: '기하',
      sub_topic: '피타고라스의 정리',
      subtypes: ['피타고라스 정리의 기본 개념', '직각삼각형의 변의 길이 구하기', '입체도형에서의 피타고라스 활용']
    },
    {
      id: 2,
      major_topic: '수와 연산',
      sub_topic: '유리수와 순환소수',
      subtypes: ['유리수의 소수 표현', '순환소수를 분수로 나타내기']
    }
  ]);

  // 새 단원 입력 폼 state
  const [newMajor, setNewMajor] = useState('');
  const [newSub, setNewSub] = useState('');
  const [isResearching, setIsResearching] = useState(false);

  // 5. 모니터링 로그
  const [isGenerating, setIsGenerating] = useState(false);
  const [logs, setLogs] = useState([
    '🟢 시스템 준비 완료. 학교급/학년/학기 및 단원 리스트를 구성하세요.'
  ]);

  // WebSocket 연결
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

  // API 키 저장 핸들러
  const handleSaveApiKeys = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/config/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          openai_api_key: openaiKey,
          gemini_api_key: geminiKey
        })
      });
      const data = await res.json();
      setKeySavedMsg('✅ API 키가 성공적으로 반영되었습니다!');
      setTimeout(() => setKeySavedMsg(''), 3000);
    } catch (err) {
      setKeySavedMsg('❌ API 키 저장 실패 (백엔드 서버 확인)');
    }
  };

  // 단원 추가 & 세부유형 리서치 실행
  const handleAddTopicWithResearch = async () => {
    if (!newMajor || !newSub) {
      alert('대단원과 중단원 명칭을 모두 입력해 주세요.');
      return;
    }
    setIsResearching(true);
    setLogs((prev) => [...prev, `🔍 단원 세부 유형 자동 리서치 중... (${newMajor} > ${newSub})`]);
    
    try {
      const res = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ major_topic: newMajor, sub_topic: newSub })
      });
      const data = await res.json();
      const extracted = data.subtypes || [];

      const newEntry = {
        id: Date.now(),
        major_topic: newMajor,
        sub_topic: newSub,
        subtypes: extracted
      };

      setTopicList([...topicList, newEntry]);
      setNewMajor('');
      setNewSub('');
      setLogs((prev) => [...prev, `✅ 단원 추가 완료: [${newMajor}] ${newSub} (유형 ${extracted.length}개)`]);
    } catch (err) {
      setLogs((prev) => [...prev, `❌ 리서치 크롤링 오류`]);
    } finally {
      setIsResearching(false);
    }
  };

  const handleRemoveTopic = (id) => {
    setTopicList(topicList.filter((item) => item.id !== id));
  };

  // 문제집 일괄 생성 및 한글 HWP RPA 실행
  const handleGenerateWorkbook = async () => {
    if (topicList.length === 0) {
      alert('문제집으로 제작할 단원을 최소 1개 이상 추가해 주세요.');
      return;
    }
    setIsGenerating(true);
    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          school_level: schoolLevel,
          grade: grade,
          semester: semester,
          topic_list: topicList.map(({ major_topic, sub_topic, subtypes }) => ({
            major_topic,
            sub_topic,
            subtypes
          })),
          model_name: modelName,
          temperature: parseFloat(temperature),
          custom_prompt: customPrompt,
          count_per_topic: parseInt(countPerTopic),
          run_rpa: runRpa
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setLogs((prev) => [...prev, `🎉 [${schoolLevel} ${grade} ${semester}] 전체 ${data.question_count}개 문항 생성 및 저장 완료!`]);
      }
    } catch (err) {
      setLogs((prev) => [...prev, `❌ 문제집 생성 중 오류가 발생했습니다.`]);
    } finally {
      setIsGenerating(false);
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
            학교급·학년·학기별 단원 목차 일괄 구성 & Antigravity 2.0 물리적 GUI (한글 HWP) 포그라운드 타이핑
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-full text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          시스템 정상 준비됨
        </div>
      </header>

      {/* 상단 2열 영역: [1] 학교급/학년/학기 & AI API KEY 창 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 학교급, 학년, 학기 선택 섹션 */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h2 className="text-base font-bold text-cyan-300 border-b border-slate-700/50 pb-2 flex items-center gap-2">
            🏫 1. 대상 학교급, 학년, 학기 설정
          </h2>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">학교급</label>
              <select
                value={schoolLevel}
                onChange={(e) => setSchoolLevel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="초등학교">초등학교</option>
                <option value="중학교">중학교</option>
                <option value="고등학교">고등학교</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">학년</label>
              <select
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="1학년">1학년</option>
                <option value="2학년">2학년</option>
                <option value="3학년">3학년</option>
                {schoolLevel === '초등학교' && (
                  <>
                    <option value="4학년">4학년</option>
                    <option value="5학년">5학년</option>
                    <option value="6학년">6학년</option>
                  </>
                )}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">학기</label>
              <select
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
              >
                <option value="1학기">1학기</option>
                <option value="2학기">2학기</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI API KEY 전용 입력 창 */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 border border-amber-500/20">
          <div className="flex justify-between items-center border-b border-slate-700/50 pb-2">
            <h2 className="text-base font-bold text-amber-300 flex items-center gap-2">
              🔑 2. AI API KEY 전용 설정 창
            </h2>
            {keySavedMsg && <span className="text-xs text-emerald-400 font-semibold">{keySavedMsg}</span>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">OpenAI API Key</label>
              <input
                type="password"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Google Gemini API Key</label>
              <input
                type="password"
                placeholder="AIzaSy..."
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>
          <button
            onClick={handleSaveApiKeys}
            className="w-full bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 text-xs font-semibold py-2 rounded-lg transition duration-200"
          >
            💾 API KEY 적용 및 저장
          </button>
        </div>
      </div>

      {/* 메인 2컬럼 레이아웃 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 왼쪽 7컬럼: 단원 리스트 관리 및 생성 설정 */}
        <div className="lg:col-span-7 space-y-6">
          {/* 단원 목록 리스트 구성 (실제 문제집 목차 관리) */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-cyan-300 border-b border-slate-700/50 pb-2">
              📚 3. 문제집 단원 목차 관리 (리스트 구성)
            </h2>

            {/* 새 단원 추가 폼 */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="대단원 (예: 기하)"
                value={newMajor}
                onChange={(e) => setNewMajor(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-cyan-500"
              />
              <input
                type="text"
                placeholder="중단원 (예: 피타고라스의 정리)"
                value={newSub}
                onChange={(e) => setNewSub(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-cyan-500"
              />
              <button
                onClick={handleAddTopicWithResearch}
                disabled={isResearching}
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition disabled:opacity-50"
              >
                {isResearching ? '🔍 리서치 중...' : '+ 단원 추가'}
              </button>
            </div>

            {/* 단원 리스트 목차 렌더링 */}
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {topicList.map((item, idx) => (
                <div key={item.id} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="bg-blue-500/20 text-blue-400 text-[11px] font-bold px-2 py-0.5 rounded">
                        단원 {idx + 1}
                      </span>
                      <span className="text-sm font-semibold text-slate-200">
                        [{item.major_topic}] {item.sub_topic}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveTopic(item.id)}
                      className="text-slate-500 hover:text-red-400 text-xs transition"
                    >
                      삭제 🗑️
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {item.subtypes.map((st, stIdx) => (
                      <span key={stIdx} className="bg-slate-800 text-slate-400 text-[10px] px-2 py-0.5 rounded">
                        • {st}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI 생성 옵션 및 실행 */}
          <div className="glass-panel p-6 rounded-2xl space-y-4 border border-indigo-500/30">
            <h2 className="text-base font-bold text-indigo-300 border-b border-slate-700/50 pb-2">
              🚀 4. 문제집 일괄 생성 및 한글(HWP) 물리 자동화
            </h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">AI 모델</label>
                <select
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none"
                >
                  <option value="GPT-4o">GPT-4o (OpenAI)</option>
                  <option value="o3-mini">o3-mini (OpenAI)</option>
                  <option value="Gemini-3.1-Pro">Gemini 3.1 Pro (Google)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">단원당 문항 수</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={countPerTopic}
                  onChange={(e) => setCountPerTopic(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none"
                />
              </div>
            </div>

            <label className="flex items-center gap-2 text-xs font-semibold text-slate-300 cursor-pointer pt-1">
              <input
                type="checkbox"
                checked={runRpa}
                onChange={(e) => setRunRpa(e.target.checked)}
                className="rounded border-slate-700 text-indigo-500"
              />
              한글(HWP) 포그라운드 물리 타이핑 & 이미지 자동 삽입 구동
            </label>

            <button
              onClick={handleGenerateWorkbook}
              disabled={isGenerating}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-3 rounded-xl transition duration-200 shadow-lg shadow-emerald-500/20 text-sm disabled:opacity-50"
            >
              {isGenerating ? '⚡ 문제집 일괄 생성 진행 중...' : `✨ [${schoolLevel} ${grade} ${semester}] 문제집 일괄 제작 및 한글 입력 시작`}
            </button>
          </div>
        </div>

        {/* 오른쪽 5컬럼: 실시간 모니터링 콘솔 */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-2xl space-y-4 h-[580px] flex flex-col">
            <div className="flex justify-between items-center border-b border-slate-700/50 pb-2">
              <h2 className="text-base font-bold text-emerald-400 flex items-center gap-2">
                📡 실시간 백엔드 & RPA 콘솔
              </h2>
              <span className="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded font-mono border border-red-500/30">
                Kill-Switch: Ctrl+Shift+F12
              </span>
            </div>
            
            <div className="flex-1 bg-slate-950 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-y-auto space-y-2 border border-slate-800/80">
              {logs.map((log, i) => (
                <div key={i} className="leading-relaxed whitespace-pre-wrap border-b border-slate-900 pb-1">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

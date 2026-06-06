"""
Production validation tests for Retirement Blueprint 101.
Run with: python production_validation_tests.py
"""
import ast
import re
import sys
import types
import importlib.util
from pathlib import Path

APP_PATH = Path('/mnt/data/app.py')
DB_PATH = Path('/mnt/data/db.py')
REQ_PATH = Path('/mnt/data/requirements.txt')

class SessionState(dict):
    def __getattr__(self, k):
        try: return self[k]
        except KeyError: raise AttributeError(k)
    def __setattr__(self, k, v): self[k] = v

class Dummy:
    def __init__(self, ret=None): self.ret = ret
    def __call__(self, *a, **k): return self.ret if self.ret is not None else self
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def __iter__(self): return iter([])
    def __bool__(self): return False
    def __getitem__(self, k): return None
    def __getattr__(self, k): return self

class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__('streamlit')
        self.session_state = SessionState()
        self.secrets = {'SUPABASE_URL':'https://dummy.supabase.co','SUPABASE_KEY':'dummy','OPENAI_API_KEY':''}
        self.sidebar = Dummy()
    def set_page_config(self,*a,**k): pass
    def markdown(self,*a,**k): pass
    def write(self,*a,**k): pass
    def caption(self,*a,**k): pass
    def info(self,*a,**k): pass
    def warning(self,*a,**k): pass
    def error(self,*a,**k): pass
    def success(self,*a,**k): pass
    def toast(self,*a,**k): pass
    def divider(self,*a,**k): pass
    def subheader(self,*a,**k): pass
    def header(self,*a,**k): pass
    def title(self,*a,**k): pass
    def dataframe(self,*a,**k): pass
    def plotly_chart(self,*a,**k): pass
    def pyplot(self,*a,**k): pass
    def download_button(self,*a,**k): return False
    def button(self,*a,**k): return False
    def form_submit_button(self,*a,**k): return False
    def toggle(self,label, value=False, *a, **k): return value
    def checkbox(self,label, value=False, *a, **k): return value
    def radio(self,label, options, index=0, *a, **k): return options[index] if options else None
    def selectbox(self,label, options, index=0, *a, **k): return options[index] if options else None
    def slider(self,label, min_value=None, max_value=None, value=None, *a, **k): return value if value is not None else min_value
    def number_input(self,label, min_value=None, max_value=None, value=0, *a, **k): return value
    def text_input(self,label, value='', *a, **k): return value
    def text_area(self,label, value='', *a, **k): return value
    def columns(self, spec, *a, **k):
        n = spec if isinstance(spec,int) else len(spec)
        return [Dummy() for _ in range(n)]
    def tabs(self, labels): return [Dummy() for _ in labels]
    def expander(self,*a,**k): return Dummy()
    def form(self,*a,**k): return Dummy()
    def container(self,*a,**k): return Dummy()
    def cache_resource(self, f=None, **k):
        def deco(fn): return fn
        return deco(f) if f else deco
    def cache_data(self, f=None, **k):
        def deco(fn): return fn
        return deco(f) if f else deco
    def rerun(self): pass
    def __getattr__(self,k): return Dummy()

def import_app():
    sys.path.insert(0, '/mnt/data')
    fake_st = FakeStreamlit()
    sys.modules['streamlit'] = fake_st
    components = types.ModuleType('streamlit.components')
    v1 = types.ModuleType('streamlit.components.v1')
    v1.html = lambda *a, **k: None
    components.v1 = v1
    sys.modules['streamlit.components'] = components
    sys.modules['streamlit.components.v1'] = v1
    supabase_mod = types.ModuleType('supabase')
    class FakeTable:
        def __init__(self): self.data=[]
        def __getattr__(self,k): return lambda *a, **kw: self
        def execute(self): return types.SimpleNamespace(data=[])
    class FakeClient:
        def table(self,*a,**k): return FakeTable()
        @property
        def auth(self): return FakeTable()
    supabase_mod.create_client = lambda url, key: FakeClient()
    sys.modules['supabase'] = supabase_mod
    spec = importlib.util.spec_from_file_location('app_under_test', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['app_under_test'] = mod
    spec.loader.exec_module(mod)
    return mod, fake_st

RESULTS=[]
def check(name, fn):
    try:
        fn()
        RESULTS.append((name, 'PASS', ''))
    except AssertionError as e:
        RESULTS.append((name, 'FAIL', str(e)))
    except Exception as e:
        RESULTS.append((name, 'ERROR', repr(e)))

def assert_close(actual, expected, tol=1e-6):
    assert abs(actual - expected) <= tol, f'expected {expected}, got {actual}'

text = APP_PATH.read_text(encoding='utf-8')
tree = ast.parse(text)

def test_ast():
    assert tree is not None

def test_requirements():
    req = REQ_PATH.read_text().splitlines()
    for pkg in ['streamlit','pandas','numpy','plotly','openai','supabase==2.10.0','httpx==0.27.2','matplotlib','reportlab']:
        assert pkg in req, f'missing {pkg}'

def test_no_patch_overwrite():
    assert 'Retirement Blueprint 101 safe patch script' not in text, 'app.py appears overwritten by patch script'

def test_navigation_targets_valid():
    valid = {'Home','Guided Questions','Budget Builder','Review Answers','Retirement Dashboard','Recommendations','Projection Table','Saved Scenarios','Retirement Age Optimizer','Monte Carlo Analysis','Stress Tests','Best Places to Retire','PDF Report','AI Retirement Coach','Resources','Help / Instructions','Legal / Disclaimers'}
    targets = re.findall(r'go_to_page\("([^"]+)"\)', text)
    bad = sorted(set(t for t in targets if t not in valid))
    assert not bad, f'bad go_to_page targets: {bad}'

def test_no_known_old_navigation_bug():
    assert 'go_to_page("Action Plan")' not in text

def test_no_known_old_projection_column_bug():
    assert '"Portfolio Need"' in text and '"Portfolio Withdrawal"' in text

def test_import_app_no_runtime_error():
    import_app()

def test_tax_math():
    mod, st = import_app()
    st.session_state.tax_year = 2026
    st.session_state.filing_status = 'married_joint'
    # $100,000 ordinary income MFJ less $32,200 deduction = $67,800 taxable.
    # 10% first $24,800 = $2,480; 12% next $43,000 = $5,160; total = $7,640.
    out = mod.estimate_federal_tax(100000, social_security_income=0)
    assert_close(out['taxable_income'], 67800)
    assert_close(out['federal_tax'], 7640)

def test_social_security_claim_age_math():
    mod, st = import_app()
    assert_close(mod.estimate_social_security_by_claim_age(2000, 62), 2000)
    assert_close(round(mod.estimate_social_security_by_claim_age(2000, 67), 2), round(2000/0.70, 2))
    assert_close(round(mod.estimate_social_security_by_claim_age(2000, 70), 2), round((2000/0.70)*1.24, 2))

def test_rmd_math():
    mod, st = import_app()
    st.session_state.rmd_start_age = 73
    assert_close(mod.calculate_required_minimum_distribution(72, 1000000), 0)
    assert_close(round(mod.calculate_required_minimum_distribution(73, 1000000), 2), round(1000000/26.5, 2))

def test_projection_basic_no_gap_before_retirement():
    mod, st = import_app()
    st.session_state.current_age = 60
    st.session_state.retire_age = 62
    st.session_state.end_age = 65
    st.session_state.traditional = 500000
    st.session_state.roth = 100000
    st.session_state.taxable = 50000
    st.session_state.cash = 20000
    st.session_state.flat_monthly_spending = 4000
    st.session_state.budget_mode = 'Flat monthly number'
    st.session_state.growth_return = 0.0
    st.session_state.safe_return = 0.0
    st.session_state.inflation = 0.0
    st.session_state.user_ss = 24000
    st.session_state.user_ss_age = 62
    df = mod.run_projection()
    assert len(df) == 6, f'expected ages 60-65 inclusive; got {len(df)}'
    assert 'Portfolio Withdrawal' in df.columns
    assert 'Portfolio Need' in df.columns
    assert_close(df.loc[df['Age']==60, 'Total Spending'].iloc[0], 0)
    assert_close(df.loc[df['Age']==62, 'Social Security'].iloc[0], 24000)
    assert df.loc[df['Age']==62, 'Portfolio Withdrawal'].iloc[0] >= 0

def test_spending_change():
    mod, st = import_app()
    st.session_state.budget_mode='Flat monthly number'
    st.session_state.flat_monthly_spending=5000
    st.session_state.enable_spending_change=True
    st.session_state.spending_change_age=70
    st.session_state.spending_change_monthly=3500
    assert_close(mod.annual_spending_for_age(69), 60000)
    assert_close(mod.annual_spending_for_age(70), 42000)

def test_basic_blueprint_snapshot():
    mod, st = import_app()
    st.session_state.current_age=55
    st.session_state.retire_age=62
    st.session_state.end_age=90
    st.session_state.traditional=400000
    st.session_state.roth=100000
    st.session_state.taxable=50000
    st.session_state.cash=25000
    st.session_state.flat_monthly_spending=4500
    st.session_state.monthly_spending=4500
    st.session_state.budget_mode='Flat monthly number'
    st.session_state.user_ss=30000
    st.session_state.user_ss_age=62
    snap = mod.calculate_basic_blueprint_snapshot()
    assert isinstance(snap, dict)
    for k in ['score','status','status_note','money_left','monthly_gap']:
        assert k in snap, f'missing {k}'

for name, fn in list(globals().items()):
    if name.startswith('test_'):
        check(name, fn)

for row in RESULTS:
    print(f'{row[1]:5} {row[0]} {row[2]}')

fails=[r for r in RESULTS if r[1] != 'PASS']
if fails:
    raise SystemExit(1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import random

try:
    from backend.config import IMAGES_DIR
except ImportError:
    from config import IMAGES_DIR

class MathRenderer:
    """
    수학 문제용 시각 자료(도형, 함수 그래프, 수직선, 3D 입체) 렌더러.
    문제의 수치 및 메타데이터(diagram_spec)를 받아 고화질 300DPI 이미지로 동적 생성합니다.
    """

    @staticmethod
    def render_latex(latex_str: str, filename: str) -> Path:
        """LaTeX 수식 코드를 투명 배경 300DPI PNG로 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(4, 1.5), dpi=300)
        ax.axis('off')
        ax.text(0.5, 0.5, f"${latex_str}$", size=18, ha='center', va='center', color='#1e293b')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_right_triangle(filename: str, label_a="a", label_b="b", label_c="c") -> Path:
        """직각삼각형 렌더링 (동적 변 길이 및 기호 바인딩)"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.8, 3.2), dpi=300)
        
        # 삼각형 외곽선
        ax.plot([0, 4, 0, 0], [0, 0, 3, 0], color='#2563eb', linewidth=2.8)
        # 직각 표시 (원점 위치)
        ax.plot([0, 0.4, 0.4], [0.4, 0.4, 0], color='#dc2626', linewidth=1.8)
        
        # 라벨 표기
        ax.text(2, -0.45, f'${label_a}$', fontsize=13, ha='center', va='top', color='#0f172a', weight='bold')
        ax.text(-0.45, 1.5, f'${label_b}$', fontsize=13, ha='right', va='center', color='#0f172a', weight='bold')
        ax.text(2.2, 1.75, f'${label_c}$', fontsize=13, ha='left', va='bottom', color='#dc2626', weight='bold')
        
        # 꼭짓점 기호
        ax.text(-0.3, -0.3, 'C', fontsize=11, color='#475569')
        ax.text(4.2, -0.3, 'B', fontsize=11, color='#475569')
        ax.text(-0.3, 3.2, 'A', fontsize=11, color='#475569')

        ax.set_xlim(-0.9, 4.9)
        ax.set_ylim(-0.9, 3.9)
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_circle_sector(filename: str, angle=60, radius_label="r", arc_label="") -> Path:
        """원 및 부채꼴 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.8, 3.8), dpi=300)
        
        # 배경 점선 원
        circle = plt.Circle((0, 0), 2, color='#94a3b8', fill=False, linestyle='--', linewidth=1.2)
        ax.add_patch(circle)
        
        # 부채꼴 호
        rad = np.radians(float(angle))
        theta = np.linspace(0, rad, 60)
        x = 2 * np.cos(theta)
        y = 2 * np.sin(theta)
        
        # 반지름 선 및 호
        ax.plot([0, 2], [0, 0], color='#059669', linewidth=2.5)
        ax.plot([0, 2 * np.cos(rad)], [0, 2 * np.sin(rad)], color='#059669', linewidth=2.5)
        ax.plot(x, y, color='#059669', linewidth=2.8)
        
        # 중심점 및 라벨
        ax.plot(0, 0, 'o', color='#0f172a', markersize=5)
        ax.text(-0.25, -0.25, 'O', fontsize=12, color='#0f172a', weight='bold')
        ax.text(1, -0.3, f'${radius_label}$', fontsize=12, ha='center', color='#0f172a', weight='bold')
        ax.text(0.5, 0.25, f'${angle}^\circ$', fontsize=11, color='#dc2626', weight='bold')

        if arc_label:
            ax.text(2.2 * np.cos(rad / 2), 2.2 * np.sin(rad / 2), f'${arc_label}$', fontsize=11, color='#059669')

        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_cube_3d(filename: str, side_label="a", diag_label="d") -> Path:
        """3D 입체도형(정육면체/직육면체) 렌더링"""
        output_path = IMAGES_DIR / filename
        fig = plt.figure(figsize=(3.8, 3.8), dpi=300)
        ax = fig.add_subplot(111, projection='3d')
        
        # 모서리 렌더링
        r = [0, 2]
        for x in r:
            for y in r:
                ax.plot([x, x], [y, y], [0, 2], color='#4f46e5', linewidth=2)
                ax.plot([x, x], [0, 2], [y, y], color='#4f46e5', linewidth=2)
                ax.plot([0, 2], [x, x], [y, y], color='#4f46e5', linewidth=2)
                
        # 대각선
        ax.plot([0, 2], [0, 2], [0, 2], color='#dc2626', linestyle='--', linewidth=2.2)
        ax.text(1, 1, 1.1, f'${diag_label}$', fontsize=12, color='#dc2626', weight='bold')
        ax.text(1, -0.3, 0, f'${side_label}$', fontsize=12, color='#4f46e5', weight='bold')
        
        ax.axis('off')
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_coordinate_graph(filename: str, slope=1.0, intercept=0.0, is_quadratic=False, a=1.0, b=0.0, c=0.0) -> Path:
        """좌표평면 1차 및 2차 함수 그래프 동적 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.8, 3.8), dpi=300)
        
        # 축
        ax.axhline(0, color='#64748b', linewidth=1.4)
        ax.axvline(0, color='#64748b', linewidth=1.4)
        
        x = np.linspace(-4, 4, 150)
        if is_quadratic:
            y = a * (x**2) + b * x + c
            label_str = f'y={a}x^2' if b == 0 and c == 0 else f'y={a}x^2+{b}x+{c}'
            line_color = '#ea580c'
        else:
            y = slope * x + intercept
            sign = '+' if intercept >= 0 else ''
            label_str = f'y={slope}x{sign}{intercept}' if intercept != 0 else f'y={slope}x'
            line_color = '#d97706'

        ax.plot(x, y, color=line_color, linewidth=2.6, label=f'${label_str}$')
        ax.grid(True, linestyle=':', alpha=0.5)
        
        ax.text(4.2, 0.1, 'x', fontsize=12, weight='bold')
        ax.text(0.15, 4.2, 'y', fontsize=12, weight='bold')
        ax.text(-0.35, -0.35, 'O', fontsize=11)
        
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4.5, 4.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_number_line(filename: str, points=None) -> Path:
        """수직선 동적 렌더링"""
        if points is None:
            points = [(-2, "A"), (3, "B")]

        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(4.5, 1.4), dpi=300)
        
        ax.plot([-5, 5], [0, 0], color='#1e293b', linewidth=2.2)
        # 화살표
        ax.plot([5, 4.8], [0, 0.12], color='#1e293b', linewidth=2)
        ax.plot([5, 4.8], [0, -0.12], color='#1e293b', linewidth=2)
        ax.plot([-5, -4.8], [0, 0.12], color='#1e293b', linewidth=2)
        ax.plot([-5, -4.8], [0, -0.12], color='#1e293b', linewidth=2)
        
        # 눈금
        for x in range(-4, 5):
            ax.plot([x, x], [-0.08, 0.08], color='#64748b', linewidth=1)
            ax.text(x, -0.28, str(x), fontsize=9, ha='center', color='#64748b')

        # 동적 지정 점 표기
        colors = ['#2563eb', '#dc2626', '#059669', '#d97706']
        for idx, (val, name) in enumerate(points):
            c = colors[idx % len(colors)]
            ax.plot([val], [0], 'o', color=c, markersize=8)
            ax.text(val, 0.25, f'{name}({val})', fontsize=11, ha='center', color=c, weight='bold')
        
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-0.7, 0.7)
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @classmethod
    def render_custom_spec(cls, spec: dict, filename: str) -> Path:
        """AI 또는 동적 엔진이 반환한 spec 객체를 기반으로 도식 렌더링"""
        dtype = spec.get("type", "right_triangle")
        if dtype == "right_triangle":
            return cls.render_right_triangle(
                filename, 
                label_a=spec.get("label_a", "a"), 
                label_b=spec.get("label_b", "b"), 
                label_c=spec.get("label_c", "c")
            )
        elif dtype == "circle_sector":
            return cls.render_circle_sector(
                filename, 
                angle=spec.get("angle", 60), 
                radius_label=spec.get("radius_label", "r"),
                arc_label=spec.get("arc_label", "")
            )
        elif dtype == "cube_3d":
            return cls.render_cube_3d(
                filename, 
                side_label=spec.get("side_label", "a"), 
                diag_label=spec.get("diag_label", "d")
            )
        elif dtype == "coordinate_graph":
            return cls.render_coordinate_graph(
                filename, 
                slope=spec.get("slope", 1.0), 
                intercept=spec.get("intercept", 0.0),
                is_quadratic=spec.get("is_quadratic", False),
                a=spec.get("a", 1.0),
                b=spec.get("b", 0.0),
                c=spec.get("c", 0.0)
            )
        elif dtype == "number_line":
            pts = spec.get("points", [(-2, "A"), (3, "B")])
            return cls.render_number_line(filename, points=pts)
        else:
            latex_expr = spec.get("latex", r"a^2 + b^2 = c^2")
            return cls.render_latex(latex_expr, filename)

    @classmethod
    def render_auto_by_topic(cls, major_topic: str, sub_topic: str, q_index: int, filename: str, spec: dict = None) -> Path:
        """명시적 spec이 있으면 우선 사용하고, 없으면 무작위성을 부여하여 무조건 다채로운 도식 생성"""
        if spec:
            try:
                return cls.render_custom_spec(spec, filename)
            except Exception:
                pass

        # 무작위 변수 조합 기반 동적 도식 렌더링
        rnd = random.Random(q_index * 137 + len(major_topic) * 17)
        choice = rnd.choice(["right_triangle", "circle_sector", "cube_3d", "coordinate_graph", "number_line"])
        
        if choice == "right_triangle":
            triples = [(3, 4, "x"), (6, 8, "x"), (5, 12, "x"), ("a", "b", "c"), ("x", 12, 13)]
            t = rnd.choice(triples)
            return cls.render_right_triangle(filename, label_a=str(t[0]), label_b=str(t[1]), label_c=str(t[2]))
        elif choice == "circle_sector":
            angles = [30, 45, 60, 90, 120, 135, 150]
            radii = ["r", "2", "3", "5", "R"]
            return cls.render_circle_sector(filename, angle=rnd.choice(angles), radius_label=rnd.choice(radii))
        elif choice == "cube_3d":
            sides = ["a", "x", "3", "4", "5"]
            diags = ["l", "d", "3\\sqrt{3}", "x"]
            return cls.render_cube_3d(filename, side_label=rnd.choice(sides), diag_label=rnd.choice(diags))
        elif choice == "coordinate_graph":
            is_quad = rnd.choice([True, False])
            slopes = [-2, -1, 0.5, 1, 2]
            intercepts = [-3, -1, 1, 2, 3]
            return cls.render_coordinate_graph(filename, slope=rnd.choice(slopes), intercept=rnd.choice(intercepts), is_quadratic=is_quad, a=rnd.choice([1, -1, 0.5]))
        else:
            p1 = rnd.randint(-4, -1)
            p2 = rnd.randint(1, 4)
            labels = [("A", "B"), ("P", "Q"), ("M", "N")]
            lbl = rnd.choice(labels)
            return cls.render_number_line(filename, points=[(p1, lbl[0]), (p2, lbl[1])])

renderer = MathRenderer()

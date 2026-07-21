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
        """직각삼각형 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.5, 3), dpi=300)
        
        ax.plot([0, 4, 0, 0], [0, 0, 3, 0], color='#2563eb', linewidth=2.5)
        # 직각 표시
        ax.plot([0, 0.4, 0.4], [0.4, 0.4, 0], color='#dc2626', linewidth=1.5)
        
        ax.text(2, -0.4, f'${label_a}$', fontsize=13, ha='center', color='#1e293b')
        ax.text(-0.4, 1.5, f'${label_b}$', fontsize=13, va='center', color='#1e293b')
        ax.text(2.1, 1.7, f'${label_c}$', fontsize=13, color='#1e293b')
        
        ax.set_xlim(-0.8, 4.8)
        ax.set_ylim(-0.8, 3.8)
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_circle_sector(filename: str, angle=60, radius_label="r") -> Path:
        """원 및 부채꼴 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)
        
        # 원 그리기
        circle = plt.Circle((0, 0), 2, color='#cbd5e1', fill=False, linestyle='--', linewidth=1.5)
        ax.add_patch(circle)
        
        # 부채꼴 호
        rad = np.radians(angle)
        theta = np.linspace(0, rad, 50)
        x = 2 * np.cos(theta)
        y = 2 * np.sin(theta)
        
        ax.plot([0, 2], [0, 0], color='#059669', linewidth=2.5)
        ax.plot([0, 2 * np.cos(rad)], [0, 2 * np.sin(rad)], color='#059669', linewidth=2.5)
        ax.plot(x, y, color='#059669', linewidth=2.5)
        
        ax.text(1, -0.3, f'${radius_label}$', fontsize=12, ha='center', color='#1e293b')
        ax.text(0.5, 0.2, f'${angle}^\circ$', fontsize=11, color='#dc2626')
        ax.plot(0, 0, 'o', color='#1e293b', markersize=4)
        ax.text(-0.3, -0.3, 'O', fontsize=12, color='#1e293b')
        
        ax.set_xlim(-2.3, 2.3)
        ax.set_ylim(-2.3, 2.3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_cube_3d(filename: str, label="x") -> Path:
        """3D 입체도형(정육면체) 렌더링"""
        output_path = IMAGES_DIR / filename
        fig = plt.figure(figsize=(3.5, 3.5), dpi=300)
        ax = fig.add_subplot(111, projection='3d')
        
        # 정육면체 뼈대
        r = [0, 2]
        for x in r:
            for y in r:
                ax.plot([x, x], [y, y], [0, 2], color='#4f46e5', linewidth=2)
                ax.plot([x, x], [0, 2], [y, y], color='#4f46e5', linewidth=2)
                ax.plot([0, 2], [x, x], [y, y], color='#4f46e5', linewidth=2)
                
        # 대각선 표시
        ax.plot([0, 2], [0, 2], [0, 2], color='#dc2626', linestyle='--', linewidth=2)
        ax.text(1, 1, 1, f'd', fontsize=12, color='#dc2626', weight='bold')
        
        ax.axis('off')
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_coordinate_graph(filename: str, slope=1, intercept=1) -> Path:
        """좌표평면 및 1차/2차 함수 그래프 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)
        
        x = np.linspace(-3, 3, 100)
        y = slope * x + intercept
        
        # 축
        ax.axhline(0, color='#64748b', linewidth=1.2)
        ax.axvline(0, color='#64748b', linewidth=1.2)
        
        # 그래프
        ax.plot(x, y, color='#d97706', linewidth=2.5, label=f'y={slope}x+{intercept}')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.text(3.2, 0, 'x', fontsize=11)
        ax.text(0.1, 3.2, 'y', fontsize=11)
        ax.text(-0.3, -0.3, 'O', fontsize=11)
        
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3.5, 3.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @staticmethod
    def render_number_line(filename: str, p1=-2, p2=3) -> Path:
        """수직선 렌더링"""
        output_path = IMAGES_DIR / filename
        fig, ax = plt.subplots(figsize=(4, 1.2), dpi=300)
        
        ax.plot([-4, 4], [0, 0], color='#1e293b', linewidth=2)
        # 화살표
        ax.plot([4, 3.8], [0, 0.1], color='#1e293b', linewidth=2)
        ax.plot([4, 3.8], [0, -0.1], color='#1e293b', linewidth=2)
        
        # 점 표기
        ax.plot([p1, p2], [0, 0], 'o', color='#2563eb', markersize=7)
        ax.text(p1, -0.3, f'A({p1})', fontsize=11, ha='center', color='#2563eb', weight='bold')
        ax.text(p2, -0.3, f'B({p2})', fontsize=11, ha='center', color='#2563eb', weight='bold')
        
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-0.8, 0.8)
        ax.axis('off')
        
        plt.savefig(output_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)
        return output_path

    @classmethod
    def render_auto_by_topic(cls, major_topic: str, sub_topic: str, q_index: int, filename: str) -> Path:
        """단원 및 문항 번호에 따라 가장 적합하고 다양성 높은 도형/그래프/수식 자동 선택 렌더링"""
        topic_combined = f"{major_topic} {sub_topic}".lower()
        
        # 기하/도형 관련
        if any(k in topic_combined for k in ["피타고라스", "직각", "삼각형", "기하"]):
            mod = q_index % 3
            if mod == 1:
                return cls.render_right_triangle(filename, label_a=f"{q_index+2}", label_b=f"{q_index+4}", label_c="x")
            elif mod == 2:
                return cls.render_cube_3d(filename, label="a")
            else:
                return cls.render_circle_sector(filename, angle=30 * (q_index % 4 + 1))
        # 함수/좌표 관련
        elif any(k in topic_combined for k in ["함수", "좌표", "방정식", "연립"]):
            return cls.render_coordinate_graph(filename, slope=(q_index % 3) + 1, intercept=(q_index % 2) - 1)
        # 수와 연산/수직선
        elif any(k in topic_combined for k in ["수", "연산", "유리수", "소수", "부등식"]):
            return cls.render_number_line(filename, p1=-(q_index % 4 + 1), p2=(q_index % 5 + 1))
        # 무작위 다양성
        else:
            choice = q_index % 4
            if choice == 0:
                return cls.render_right_triangle(filename, label_a="a", label_b="b", label_c="c")
            elif choice == 1:
                return cls.render_circle_sector(filename, angle=45)
            elif choice == 2:
                return cls.render_coordinate_graph(filename, slope=-1, intercept=2)
            else:
                return cls.render_latex(rf"\frac{{{q_index}}}{{x+1}} + \sqrt{{{q_index+3}}} = {q_index*2}", filename)

renderer = MathRenderer()

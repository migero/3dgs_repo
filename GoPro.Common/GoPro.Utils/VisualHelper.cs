using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Forms;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;

namespace GoPro.Utils
{
	public class VisualHelper
	{
		public struct Scale
		{
			public double X;

			public double Y;
		}

		public struct POINT
		{
			public int X;

			public int Y;
		}

		internal enum AccentState
		{
			ACCENT_DISABLED,
			ACCENT_ENABLE_GRADIENT,
			ACCENT_ENABLE_TRANSPARENTGRADIENT,
			ACCENT_ENABLE_BLURBEHIND,
			ACCENT_INVALID_STATE
		}

		internal struct AccentPolicy
		{
			public AccentState AccentState;

			public int AccentFlags;

			public int GradientColor;

			public int AnimationId;
		}

		internal struct WindowCompositionAttributeData
		{
			public WindowCompositionAttribute Attribute;

			public IntPtr Data;

			public int SizeOfData;
		}

		internal enum WindowCompositionAttribute
		{
			WCA_ACCENT_POLICY = 19
		}

		[DllImport("user32.dll")]
		public static extern void GetCursorPos(out POINT p);

		[DllImport("user32.dll")]
		internal static extern int SetWindowCompositionAttribute(IntPtr hwnd, ref WindowCompositionAttributeData data);

		public static void EnableBlur(Window window)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			WindowInteropHelper val = new WindowInteropHelper(window);
			AccentPolicy structure = new AccentPolicy
			{
				AccentState = AccentState.ACCENT_ENABLE_BLURBEHIND
			};
			int num = Marshal.SizeOf(structure);
			IntPtr intPtr = Marshal.AllocHGlobal(num);
			Marshal.StructureToPtr(structure, intPtr, fDeleteOld: false);
			WindowCompositionAttributeData data = new WindowCompositionAttributeData
			{
				Attribute = WindowCompositionAttribute.WCA_ACCENT_POLICY,
				SizeOfData = num,
				Data = intPtr
			};
			SetWindowCompositionAttribute(val.get_Handle(), ref data);
			Marshal.FreeHGlobal(intPtr);
		}

		public static Screen FindCurrentScreen()
		{
			GetCursorPos(out var p);
			return FindCurrentScreen(p.X, p.Y, 0.0, 0.0);
		}

		public static Screen FindCurrentScreen(double left, double top, double width, double height)
		{
			int x = (int)(left + width * 0.5);
			int y = (int)(top + height * 0.5);
			Screen[] allScreens = Screen.get_AllScreens();
			foreach (Screen val in allScreens)
			{
				if (val.get_Bounds().Contains(x, y))
				{
					return val;
				}
			}
			return Screen.get_PrimaryScreen();
		}

		public static Scale GetScale(Visual visual)
		{
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			Scale scale = default(Scale);
			scale.X = 1.0;
			scale.Y = 1.0;
			Scale result = scale;
			if (visual == null)
			{
				return result;
			}
			PresentationSource val = PresentationSource.FromVisual(visual);
			if (val == null)
			{
				return result;
			}
			Matrix transformToDevice = val.get_CompositionTarget().get_TransformToDevice();
			result.X = ((Matrix)(ref transformToDevice)).get_M11();
			transformToDevice = val.get_CompositionTarget().get_TransformToDevice();
			result.Y = ((Matrix)(ref transformToDevice)).get_M22();
			return result;
		}

		public static Size AdjustSizeForDPIScale(Window window, double width, double height)
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			Scale scale = GetScale((Visual)(object)window);
			width /= scale.X;
			height /= scale.Y;
			return new Size(width, height);
		}

		public static Rectangle GetScreenMaxBounds(Screen screen, bool fullscreen)
		{
			if (screen != null)
			{
				int height = (fullscreen ? screen.get_Bounds().Height : screen.get_WorkingArea().Height);
				return new Rectangle(screen.get_Bounds().Left, screen.get_Bounds().Top, screen.get_WorkingArea().Width, height);
			}
			return Rectangle.Empty;
		}

		public static void UpdateWindowPositionFromMaximized(Window window)
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			Rectangle screenMaxBounds = GetScreenMaxBounds(FindCurrentScreen(), fullscreen: false);
			Point position = Mouse.GetPosition((IInputElement)(object)window);
			double x = ((Point)(ref position)).get_X();
			double num = x / (double)screenMaxBounds.Width;
			window.set_WindowState((WindowState)0);
			double num2 = ((FrameworkElement)window).get_Width() * num;
			double left = (double)screenMaxBounds.Left + x - num2;
			window.set_Left(left);
			window.set_Top(0.0);
		}

		public static T FindVisualParent<T>(DependencyObject child) where T : DependencyObject
		{
			DependencyObject parent = VisualTreeHelper.GetParent(child);
			if (parent == null)
			{
				return default(T);
			}
			T val = (T)(object)((parent is T) ? parent : null);
			if (val != null)
			{
				return val;
			}
			return FindVisualParent<T>(parent);
		}

		public static T FindVisualChild<T>(DependencyObject parent) where T : DependencyObject
		{
			if (parent == null)
			{
				return default(T);
			}
			for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
			{
				DependencyObject child = VisualTreeHelper.GetChild(parent, i);
				if (child != null && child is T)
				{
					return (T)(object)child;
				}
				T val = FindVisualChild<T>(child);
				if (val != null)
				{
					return val;
				}
			}
			return default(T);
		}
	}
}

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;

namespace GoPro.Composition
{
	public class VisualHelper
	{
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

		public static void UpdateWindowPositionFromMaximized(Window window)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			Point position = Mouse.GetPosition((IInputElement)(object)window);
			double x = ((Point)(ref position)).get_X();
			double num = x / SystemParameters.get_PrimaryScreenWidth();
			window.set_WindowState((WindowState)0);
			double num2 = ((FrameworkElement)window).get_Width() * num;
			double left = x - num2;
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
	}
}

using System;
using System.Windows;
using System.Windows.Media.Animation;

namespace GoPro.Utils
{
	public static class AnimationHelper
	{
		public static void StartDoubleAnimation(DependencyObject element, DependencyProperty property, double to, uint timeMs, Action testDoneEvent = null)
		{
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Expected O, but got Unknown
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Expected O, but got Unknown
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0064: Expected O, but got Unknown
			DoubleAnimation val = new DoubleAnimation(to, Duration.op_Implicit(TimeSpan.FromMilliseconds(timeMs)));
			Storyboard.SetTarget((DependencyObject)(object)val, element);
			Storyboard.SetTargetProperty((DependencyObject)(object)val, new PropertyPath((object)property));
			Storyboard storyboard = new Storyboard();
			((Timeline)storyboard).add_Completed((EventHandler)delegate
			{
				storyboard.Stop();
				element.SetValue(property, (object)to);
				testDoneEvent?.Invoke();
			});
			((TimelineGroup)storyboard).get_Children().Add((Timeline)(object)val);
			storyboard.Begin();
		}
	}
}

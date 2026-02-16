using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Markup;

namespace GoPro.Controls
{
	public class Scrubber : UserControl, IComponentConnector
	{
		public delegate void SeekStartedDelegate();

		public delegate void SeekEndedDelegate();

		private ScrubberModel mModel;

		public SeekStartedDelegate SeekStarted;

		public SeekEndedDelegate SeekEnded;

		internal Slider ScrubberSlider;

		private bool _contentLoaded;

		public ulong CurrentTimeUs
		{
			get
			{
				return mModel.CurrentTimeUs;
			}
			set
			{
				mModel.CurrentTimeUs = value;
			}
		}

		public ulong DurationUs
		{
			get
			{
				return mModel.DurationUs;
			}
			set
			{
				mModel.DurationUs = value;
			}
		}

		public double Buffer
		{
			get
			{
				return mModel.Buffer;
			}
			set
			{
				mModel.Buffer = value;
			}
		}

		public event ScrubberModel.TimeUpdatedDelegate TimeUpdated
		{
			add
			{
				ScrubberModel scrubberModel = mModel;
				scrubberModel.TimeUpdated = (ScrubberModel.TimeUpdatedDelegate)Delegate.Combine(scrubberModel.TimeUpdated, value);
			}
			remove
			{
				ScrubberModel scrubberModel = mModel;
				scrubberModel.TimeUpdated = (ScrubberModel.TimeUpdatedDelegate)Delegate.Remove(scrubberModel.TimeUpdated, value);
			}
		}

		public Scrubber()
		{
			InitializeComponent();
			((FrameworkElement)this).set_DataContext((object)new ScrubberModel());
			mModel = ((FrameworkElement)this).get_DataContext() as ScrubberModel;
		}

		private void ScrubberSlider_PreviewMouseDown(object sender, MouseButtonEventArgs e)
		{
			((UIElement)ScrubberSlider).CaptureMouse();
			if (SeekStarted != null)
			{
				SeekStarted();
			}
		}

		private void ScrubberSlider_MouseMove(object sender, MouseEventArgs e)
		{
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Expected O, but got Unknown
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			if (((UIElement)ScrubberSlider).get_IsMouseCaptured())
			{
				Slider val = (Slider)sender;
				Point position = e.GetPosition((IInputElement)(object)val);
				double num = 1.0 / ((FrameworkElement)val).get_ActualWidth() * ((Point)(ref position)).get_X();
				double num2 = (double)mModel.DurationUs * num;
				mModel.CurrentTimeUs = (ulong)num2;
			}
		}

		private void ScrubberSlider_PreviewMouseUp(object sender, MouseButtonEventArgs e)
		{
			if (((UIElement)ScrubberSlider).get_IsMouseCaptured())
			{
				if (SeekEnded != null)
				{
					SeekEnded();
				}
				((UIElement)ScrubberSlider).ReleaseMouseCapture();
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/GoPro.Common;component/controls/scrubber.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Expected O, but got Unknown
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Expected O, but got Unknown
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Expected O, but got Unknown
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Expected O, but got Unknown
			if (connectionId == 1)
			{
				ScrubberSlider = (Slider)target;
				((UIElement)ScrubberSlider).add_PreviewMouseDown(new MouseButtonEventHandler(ScrubberSlider_PreviewMouseDown));
				((UIElement)ScrubberSlider).add_MouseMove(new MouseEventHandler(ScrubberSlider_MouseMove));
				((UIElement)ScrubberSlider).add_PreviewMouseUp(new MouseButtonEventHandler(ScrubberSlider_PreviewMouseUp));
			}
			else
			{
				_contentLoaded = true;
			}
		}
	}
}

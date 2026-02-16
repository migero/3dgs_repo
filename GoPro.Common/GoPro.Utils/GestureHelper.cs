using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Input;

namespace GoPro.Utils
{
	public class GestureHelper
	{
		public delegate void StartedDelagate();

		public delegate void StoppedDelagate();

		public delegate void DraggedDelagate(double x, double y);

		public delegate void RotatedDelagate(double rotation);

		public delegate void ZommedDelagate(double zoom);

		internal enum State
		{
			DRAG,
			ROTATE,
			ZOOM
		}

		private State m_State;

		public event StartedDelagate Started;

		public event StoppedDelagate Stopped;

		public event DraggedDelagate Dragged;

		public event RotatedDelagate Rotated;

		public event ZommedDelagate Zommed;

		public GestureHelper(UIElement element)
		{
			element.set_IsManipulationEnabled(true);
			element.add_ManipulationStarting((EventHandler<ManipulationStartingEventArgs>)OnManipulationStarting);
			element.add_ManipulationDelta((EventHandler<ManipulationDeltaEventArgs>)OnManipulationDelta);
			element.add_ManipulationCompleted((EventHandler<ManipulationCompletedEventArgs>)OnManipulationCompleted);
			m_State = State.DRAG;
		}

		private void OnManipulationStarting(object sender, ManipulationStartingEventArgs e)
		{
			if (this.Started != null)
			{
				this.Started();
				((RoutedEventArgs)e).set_Handled(true);
			}
		}

		private void OnManipulationDelta(object sender, ManipulationDeltaEventArgs e)
		{
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_0099: Unknown result type (might be due to invalid IL or missing references)
			//IL_0138: Unknown result type (might be due to invalid IL or missing references)
			//IL_013d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0156: Unknown result type (might be due to invalid IL or missing references)
			//IL_015b: Unknown result type (might be due to invalid IL or missing references)
			//IL_016c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0171: Unknown result type (might be due to invalid IL or missing references)
			Vector val;
			switch ((e.get_Manipulators() as ICollection<IManipulator>).Count)
			{
			case 1:
				m_State = State.DRAG;
				if (this.Dragged != null)
				{
					val = e.get_DeltaManipulation().get_Translation();
					if (((Vector)(ref val)).get_Length() != 1.0)
					{
						DraggedDelagate dragged = this.Dragged;
						val = e.get_DeltaManipulation().get_Translation();
						double x = ((Vector)(ref val)).get_X();
						val = e.get_DeltaManipulation().get_Translation();
						dragged(x, ((Vector)(ref val)).get_Y());
						((RoutedEventArgs)e).set_Handled(true);
					}
				}
				break;
			case 2:
				if (m_State == State.DRAG)
				{
					val = e.get_DeltaManipulation().get_Scale();
					double num = Math.Abs(((Vector)(ref val)).get_LengthSquared() - 2.0);
					double num2 = Math.Abs(e.get_DeltaManipulation().get_Rotation());
					if (num2 > num && num2 > 1.0)
					{
						m_State = State.ROTATE;
					}
					else if (num >= 0.1)
					{
						m_State = State.ZOOM;
					}
				}
				switch (m_State)
				{
				case State.ROTATE:
					if (this.Rotated != null)
					{
						this.Rotated(e.get_DeltaManipulation().get_Rotation());
						((RoutedEventArgs)e).set_Handled(true);
					}
					break;
				case State.ZOOM:
					if (this.Zommed != null)
					{
						val = e.get_DeltaManipulation().get_Scale();
						double num3;
						if (!(((Vector)(ref val)).get_LengthSquared() < 2.0))
						{
							val = e.get_DeltaManipulation().get_Scale();
							num3 = 0.0 - ((Vector)(ref val)).get_Length();
						}
						else
						{
							val = e.get_DeltaManipulation().get_Scale();
							num3 = ((Vector)(ref val)).get_Length();
						}
						double zoom = num3;
						this.Zommed(zoom);
						((RoutedEventArgs)e).set_Handled(true);
					}
					break;
				}
				break;
			}
		}

		private void OnManipulationCompleted(object sender, ManipulationCompletedEventArgs e)
		{
			if (this.Stopped != null)
			{
				this.Stopped();
				((RoutedEventArgs)e).set_Handled(true);
			}
		}
	}
}

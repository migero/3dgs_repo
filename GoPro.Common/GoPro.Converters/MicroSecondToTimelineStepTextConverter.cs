using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class MicroSecondToTimelineStepTextConverter : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			ulong num = (ulong)values[0];
			ulong num2 = (ulong)values[1];
			TimeSpan timeSpan = TimeSpan.FromMilliseconds(0.001 * (double)num);
			TimeSpan timeSpan2 = TimeSpan.FromMilliseconds(0.001 * (double)num2);
			string text = null;
			if (timeSpan2.TotalMinutes > 1.0)
			{
				text = $"{timeSpan.Minutes}m";
			}
			string text2 = null;
			if (timeSpan.Milliseconds > 0)
			{
				text2 = timeSpan.ToString("fff");
				int i;
				for (i = 0; text2[text2.Length - 1 - i] == '0'; i++)
				{
				}
				if (i > 0)
				{
					text2 = text2.Remove(text2.Length - i, i);
				}
			}
			string text3 = null;
			if (text2 != null || timeSpan2.TotalSeconds > 0.0)
			{
				text3 = $"{timeSpan.Seconds}";
			}
			string text4 = "";
			if (text != null)
			{
				text4 += text;
			}
			if (text3 != null)
			{
				text4 += text3;
			}
			if (text2 != null)
			{
				text4 += $".{text2}";
			}
			if (text3 != null)
			{
				text4 += "s";
			}
			return text4;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}

using System;
using System.Globalization;
using System.Windows.Controls.Primitives;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class BoolToTickPlacement : IValueConverter
	{
		public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
		{
			if ((bool)(value ?? ((object)false)))
			{
				return (object)(TickPlacement)3;
			}
			return (object)(TickPlacement)0;
		}

		public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
public static class ProgressVariants {
  public static void Build(string input, string output) {
    Directory.CreateDirectory(output);
    using (var src = new Bitmap(input)) {
      const int left = 6, originalEnd = 188, fullWidth = 183, capOffset = -4;
      string report = "segment,percent,bar_width_px,rightmost_core_x,unchanged_pixels_verified\r\n";
      using(var preview = new Bitmap(720, 640))
      using(var g = Graphics.FromImage(preview))
      using(var font = new Font("Arial", 13)) {
        g.Clear(Color.FromArgb(238,240,244));
        g.DrawString("Progress 1-19 / 20 - fixed original gradient", font, Brushes.Black, 16, 12);
        for(int n=1; n<=19; n++) {
          int width = (int)Math.Round(fullWidth*n/20.0, MidpointRounding.AwayFromZero);
          int end = left+width-1;
          int capStart = end+capOffset;
          int checkedPixels=0;
          using(var dst = new Bitmap(src.Width,src.Height,PixelFormat.Format24bppRgb)) {
            using(var dg=Graphics.FromImage(dst)) dg.Clear(Color.White);
            for(int y=0; y<src.Height; y++) {
              double baseline=0;
              for(int x=172; x<=180; x++) baseline += 255-src.GetPixel(x,y).R;
              baseline/=9.0;
              for(int x=0; x<capStart; x++) dst.SetPixel(x,y,src.GetPixel(x,y));
              for(int x=capStart; x<src.Width && x<=end+7; x++) {
                int tx=originalEnd+(x-end);
                double coverage=baseline>0.5 ? (255-src.GetPixel(tx,y).R)/baseline : 0;
                coverage=Math.Max(0,Math.Min(1,coverage));
                Color c=src.GetPixel(x,y);
                dst.SetPixel(x,y,Color.FromArgb(
                  (int)Math.Round(255-(255-c.R)*coverage),
                  (int)Math.Round(255-(255-c.G)*coverage),
                  (int)Math.Round(255-(255-c.B)*coverage)));
              }
            }
            string filename=Path.Combine(output,String.Format("progress_{0:00}_of_20_{1:00}percent.png",n,n*5));
            dst.Save(filename,ImageFormat.Png);
            using(var saved=new Bitmap(filename)) {
              if(saved.Width!=src.Width || saved.Height!=src.Height) throw new Exception("Canvas mismatch");
              for(int y=0;y<src.Height;y++) for(int x=0;x<capStart;x++) {
                if(saved.GetPixel(x,y).ToArgb()!=src.GetPixel(x,y).ToArgb()) throw new Exception("Gradient pixel changed");
                checkedPixels++;
              }
              // The center right edge must extend beyond its top and bottom corners.
              int top=LastSaturated(saved,6), middle=LastSaturated(saved,8), bottom=LastSaturated(saved,11);
              if(!(middle>top && middle>bottom)) throw new Exception("Rounded cap verification failed at "+n);
            }
            report+=String.Format("{0},{1},{2},{3},{4}\r\n",n,n*5,width,end,checkedPixels);
            int py=48+(n-1)*30;
            g.DrawString(String.Format("{0:00}/20  {1:00}%",n,n*5),font,Brushes.Black,18,py+3);
            g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
            g.PixelOffsetMode=System.Drawing.Drawing2D.PixelOffsetMode.Half;
            g.DrawImage(dst,new Rectangle(166,py,392,38),0,0,src.Width,src.Height,GraphicsUnit.Pixel);
          }
        }
        preview.Save(Path.Combine(output,"preview.png"),ImageFormat.Png);
      }
      File.WriteAllText(Path.Combine(output,"verification.csv"),report);
      File.WriteAllText(Path.Combine(output,"README.txt"),"19 PNG images, progress 1-19 of 20 (5%-95%).\r\nCanvas: 196x19 pixels, same as input. Original white background retained.\r\nThe gradient is never rescaled or recolored. Pixels before the movable cap are copied exactly from the original JPEG.\r\nRight rounded cap and glow coverage are sampled from the original right cap, then applied at the new endpoint.\r\nLengths are rounded to the nearest pixel because full bar width is 183 pixels.\r\nverification.csv records pixel equality checks for all 19 outputs.\r\n");
    }
  }
  static int LastSaturated(Bitmap im,int y) {
    int last=-1;
    for(int x=0;x<im.Width;x++) { var c=im.GetPixel(x,y); if(c.G-c.R>80 || c.B-c.R>80) last=x; }
    return last;
  }
}
'@ -ReferencedAssemblies System.Drawing
[ProgressVariants]::Build('C:\Users\traci\.codex\attachments\c82e3285-aa51-483e-bf1f-f29bccdf9218\image-1.jpg','G:\Doc\ChatGPT\New project\进度条-1至19段')
